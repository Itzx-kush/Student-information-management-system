import os
import re
import subprocess
from typing import Dict, Any, List, Optional

# Valid branch name pattern: alphanumeric, slashes, dashes, underscores
# Must not start with dash or slash, must not contain '..' or '~' or '^' or ':'
BRANCH_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9/_.-]{0,99}$')
PROTECTED_BRANCHES = {'main', 'master', 'HEAD'}

class GitService:
    """
    Safely interfaces with the local Git repository for the Student Management application.
    All operations are strictly allowlisted, parameterized, and run with shell=False.
    """

    def __init__(self, repo_path: Optional[str] = None):
        if repo_path is None:
            self.repo_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        else:
            self.repo_path = os.path.abspath(repo_path)

    def _run_git_command(self, args: List[str], timeout: int = 5) -> Dict[str, Any]:
        """
        Execute git commands safely using subprocess.run without shell=True.
        """
        # Security: ensure command starts with 'git' and args are a list of strings
        if not args or args[0] != 'git':
            return {
                'success': False,
                'output': '',
                'error': 'Invalid command specification.',
                'command': ' '.join(args) if args else ''
            }

        try:
            result = subprocess.run(
                args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                shell=False,
                timeout=timeout
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            return {
                'success': result.returncode == 0,
                'output': stdout,
                'error': stderr if result.returncode != 0 else '',
                'returncode': result.returncode,
                'command': ' '.join(args)
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after {timeout} seconds.',
                'command': ' '.join(args)
            }
        except Exception as ex:
            return {
                'success': False,
                'output': '',
                'error': f'Execution failed: {str(ex)}',
                'command': ' '.join(args)
            }

    def validate_branch_name(self, name: str) -> tuple[bool, str]:
        """
        Validate that the branch name complies with Git reference rules and safety restrictions.
        """
        if not name:
            return False, "Branch name cannot be empty."

        clean_name = name.strip()
        if len(clean_name) > 100:
            return False, "Branch name must be under 100 characters."

        if clean_name.startswith('-') or clean_name.startswith('/'):
            return False, "Branch name cannot start with a hyphen or slash."

        if '..' in clean_name or '@{' in clean_name or '\\' in clean_name or ' ' in clean_name:
            return False, "Branch name contains invalid characters (spaces, double dots, or backslashes)."

        if not BRANCH_NAME_PATTERN.match(clean_name):
            return False, "Branch name contains invalid characters. Use alphanumeric characters, hyphens, and slashes."

        return True, ""

    def get_repo_status(self) -> Dict[str, Any]:
        """Get repository status and current state."""
        current_branch = self.get_current_branch()
        branches = self.list_branches()
        commits = self.get_recent_commits(limit=8)
        status_res = self._run_git_command(['git', 'status', '--short'])
        detailed_status = self._run_git_command(['git', 'status'])
        remotes_res = self._run_git_command(['git', 'remote', '-v'])

        return {
            'is_repo': True,
            'current_branch': current_branch,
            'branches': branches,
            'recent_commits': commits,
            'status_short': status_res.get('output', ''),
            'status_full': detailed_status.get('output', ''),
            'remotes': remotes_res.get('output', ''),
            'repo_path': self.repo_path
        }

    def get_current_branch(self) -> str:
        """Returns the currently active branch name."""
        res = self._run_git_command(['git', 'branch', '--show-current'])
        if res['success'] and res['output']:
            return res['output']
        # Fallback if detached HEAD
        rev_res = self._run_git_command(['git', 'rev-parse', '--short', 'HEAD'])
        return f"detached at {rev_res['output']}" if rev_res['success'] else 'unknown'

    def list_branches(self) -> List[Dict[str, Any]]:
        """List all local branches with their active status."""
        res = self._run_git_command(['git', 'branch', '--list'])
        branches = []
        if res['success']:
            for line in res['output'].splitlines():
                line = line.strip()
                if not line:
                    continue
                is_current = line.startswith('*')
                name = line.lstrip('* ').strip()
                branches.append({
                    'name': name,
                    'is_current': is_current,
                    'is_protected': name in PROTECTED_BRANCHES
                })
        return branches

    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve recent commit history formatted for display."""
        res = self._run_git_command(['git', 'log', f'-n', str(limit), '--pretty=format:%h|%an|%ar|%s'])
        commits = []
        if res['success'] and res['output']:
            for line in res['output'].splitlines():
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3]
                    })
        return commits

    def create_branch(self, branch_name: str) -> Dict[str, Any]:
        """Safely create a new Git branch."""
        valid, msg = self.validate_branch_name(branch_name)
        if not valid:
            return {'success': False, 'error': msg, 'command': f'git branch {branch_name}'}

        # Check if branch already exists
        existing = [b['name'] for b in self.list_branches()]
        if branch_name in existing:
            return {'success': False, 'error': f"Branch '{branch_name}' already exists.", 'command': f'git branch {branch_name}'}

        return self._run_git_command(['git', 'branch', branch_name])

    def switch_branch(self, branch_name: str) -> Dict[str, Any]:
        """Safely switch to an existing Git branch."""
        valid, msg = self.validate_branch_name(branch_name)
        if not valid:
            return {'success': False, 'error': msg, 'command': f'git switch {branch_name}'}

        existing = [b['name'] for b in self.list_branches()]
        if branch_name not in existing:
            return {
                'success': False,
                'error': f"Branch '{branch_name}' does not exist. Create it first using 'git branch {branch_name}'.",
                'command': f'git switch {branch_name}'
            }

        return self._run_git_command(['git', 'switch', branch_name])

    def merge_branch(self, branch_to_merge: str) -> Dict[str, Any]:
        """Safely merge specified branch into the currently checked-out branch."""
        valid, msg = self.validate_branch_name(branch_to_merge)
        if not valid:
            return {'success': False, 'error': msg, 'command': f'git merge {branch_to_merge}'}

        current = self.get_current_branch()
        if branch_to_merge == current:
            return {
                'success': False,
                'error': f"Cannot merge branch '{branch_to_merge}' into itself.",
                'command': f'git merge {branch_to_merge}'
            }

        existing = [b['name'] for b in self.list_branches()]
        if branch_to_merge not in existing:
            return {
                'success': False,
                'error': f"Branch '{branch_to_merge}' does not exist to merge.",
                'command': f'git merge {branch_to_merge}'
            }

        return self._run_git_command(['git', 'merge', branch_to_merge, '--no-edit'])

    def delete_branch(self, branch_name: str) -> Dict[str, Any]:
        """
        Safely delete a branch.
        Enforces safety rules:
        - Never delete protected branches (main, master).
        - Never delete the currently active branch.
        - Uses safe deletion 'git branch -d'.
        """
        valid, msg = self.validate_branch_name(branch_name)
        if not valid:
            return {'success': False, 'error': msg, 'command': f'git branch -d {branch_name}'}

        if branch_name in PROTECTED_BRANCHES:
            return {
                'success': False,
                'error': f"Safety Protection: The primary branch '{branch_name}' cannot be deleted.",
                'command': f'git branch -d {branch_name}'
            }

        current = self.get_current_branch()
        if branch_name == current:
            return {
                'success': False,
                'error': f"Cannot delete branch '{branch_name}' because it is currently checked out. Switch to another branch first.",
                'command': f'git branch -d {branch_name}'
            }

        return self._run_git_command(['git', 'branch', '-d', branch_name])
