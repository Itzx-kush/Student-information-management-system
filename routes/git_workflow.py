from flask import render_template, request, redirect, url_for, flash, session, jsonify
from routes import git_bp
from services.git_service import GitService

git_service = GitService()

CHECKLIST_ITEMS = [
    {"id": "git_init", "label": "Repository Initialization (git init)", "module": "Module E / C"},
    {"id": "git_status", "label": "Checking Status & File Tracking (git status, git add)", "module": "Module D / E"},
    {"id": "git_commit", "label": "Committing Changes with Meaningful Messages (git commit)", "module": "Module D / E"},
    {"id": "git_branch", "label": "Creating and Listing Feature Branches (git branch, git switch)", "module": "Module C / A"},
    {"id": "git_merge", "label": "Merging Feature Branches into Main (git merge)", "module": "Module C / A"},
    {"id": "git_branch_del", "label": "Deleting Merged Branches (git branch -d)", "module": "Module C / A"},
    {"id": "git_remote", "label": "Configuring Remote Origin (git remote add)", "module": "Module D / B"},
    {"id": "git_push", "label": "Pushing Code to GitHub (git push -u origin main)", "module": "Module D / B"},
    {"id": "git_pull", "label": "Pulling Remote Updates (git pull origin main)", "module": "Module D / B"},
    {"id": "git_pr", "label": "Pull Request Review & Collaborative Integration", "module": "Module E / C"},
    {"id": "git_conflict", "label": "Understanding & Resolving Merge Conflicts", "module": "Module E / C"}
]

@git_bp.route('/branches')
def branches():
    """Module C (Question A): Git Branch Management educational guide and live practical panel."""
    repo_state = git_service.get_repo_status()
    return render_template(
        'git/branches.html',
        repo_state=repo_state
    )


@git_bp.route('/branches/create', methods=['POST'])
def create_branch():
    """Live Git: Safely create a branch."""
    branch_name = request.form.get('branch_name', '').strip()
    result = git_service.create_branch(branch_name)

    if result['success']:
        flash(f"Branch '{branch_name}' successfully created! (Command: {result['command']})", 'success')
    else:
        flash(f"Branch creation failed: {result.get('error', 'Unknown error')}", 'danger')

    return redirect(url_for('git.branches'))


@git_bp.route('/branches/switch', methods=['POST'])
def switch_branch():
    """Live Git: Safely switch to an existing branch."""
    branch_name = request.form.get('branch_name', '').strip()
    result = git_service.switch_branch(branch_name)

    if result['success']:
        flash(f"Switched to branch '{branch_name}'. (Command: {result['command']})", 'success')
    else:
        flash(f"Failed to switch branch: {result.get('error', 'Unknown error')}", 'danger')

    return redirect(url_for('git.branches'))


@git_bp.route('/branches/merge', methods=['POST'])
def merge_branch():
    """Live Git: Safely merge branch into current branch."""
    branch_name = request.form.get('branch_name', '').strip()
    result = git_service.merge_branch(branch_name)

    if result['success']:
        flash(f"Successfully merged '{branch_name}' into current branch! Output: {result.get('output', 'Already up to date.')}", 'success')
    else:
        flash(f"Merge failed: {result.get('error', 'Unknown error')}", 'danger')

    return redirect(url_for('git.branches'))


@git_bp.route('/branches/delete', methods=['POST'])
def delete_branch():
    """Live Git: Safely delete a branch."""
    branch_name = request.form.get('branch_name', '').strip()
    result = git_service.delete_branch(branch_name)

    if result['success']:
        flash(f"Branch '{branch_name}' deleted successfully! (Command: {result['command']})", 'success')
    else:
        flash(f"Branch deletion rejected: {result.get('error', 'Unknown error')}", 'danger')

    return redirect(url_for('git.branches'))


@git_bp.route('/workflow')
def github_workflow():
    """Module D (Question B): Git and GitHub Workflow tutorial."""
    steps = [
        {
            "step": 1,
            "title": "Create a GitHub Repository",
            "command": "gh repo create Itzx-kush/Student-information-management-system --public",
            "purpose": "Establishes a centralized remote repository on GitHub to host project source code, issues, and collaboration history.",
            "output": "✓ Created repository Itzx-kush/Student-information-management-system on GitHub\nhttps://github.com/Itzx-kush/Student-information-management-system",
            "explanation": "Before local development can be shared, an empty or initialized remote repository is provisioned on GitHub. It defines the central upstream origin."
        },
        {
            "step": 2,
            "title": "Clone the Remote Repository",
            "command": "git clone https://github.com/Itzx-kush/Student-information-management-system.git",
            "purpose": "Copies the entire remote repository, history, branches, and commit pointers to your local machine.",
            "output": "Cloning into 'Student-information-management-system'...\nremote: Enumerating objects: 3, done.\nremote: Total 3 (delta 0), reused 0 (delta 0)\nReceiving objects: 100% (3/3), done.",
            "explanation": "Creates a local working directory with a preconfigured remote named 'origin' pointing back to GitHub."
        },
        {
            "step": 3,
            "title": "Navigate & Add Application Files",
            "command": "cd Student-information-management-system\n# Create app.py, models.py, templates, static files",
            "purpose": "Places working source files into your local repository workspace.",
            "output": "Directory: D:\\Student-information-management-system\napp.py  config.py  models.py  routes/  templates/  static/",
            "explanation": "Files created in the working tree are initially untracked by Git until explicitly staged."
        },
        {
            "step": 4,
            "title": "Inspect Repository Working Tree Status",
            "command": "git status",
            "purpose": "Examines the working tree and staging area (index) to observe untracked, modified, or staged files.",
            "output": "On branch main\nUntracked files:\n  (use \"git add <file>...\" to include in what will be committed)\n\tapp.py\n\tconfig.py\n\tmodels.py\n\troutes/\n\ttemplates/\n\tstatic/",
            "explanation": "Informs the developer about files that need staging before a commit can be created."
        },
        {
            "step": 5,
            "title": "Stage Changes into Index",
            "command": "git add .",
            "purpose": "Adds changes in the working directory to the staging area, preparing them for the next commit snapshot.",
            "output": "# All untracked and modified files are staged into the Git index",
            "explanation": "Git's two-stage commit design allows you to selectively choose what goes into a commit snapshot."
        },
        {
            "step": 6,
            "title": "Record Commit Snapshot",
            "command": "git commit -m \"Add student management system\"",
            "purpose": "Permanently saves a staged snapshot to local repository history with a descriptive commit message.",
            "output": "[main a1b2c3d] Add student management system\n 12 files changed, 840 insertions(+)\n create mode 100644 app.py\n create mode 100644 models.py",
            "explanation": "Creates a cryptographically unique SHA-1 hash representing the repository state at this point in time."
        },
        {
            "step": 7,
            "title": "Inspect & Verify Remote Configuration",
            "command": "git remote -v",
            "purpose": "Verifies all configured remote repositories and their URLs for fetching and pushing.",
            "output": "origin  https://github.com/Itzx-kush/Student-information-management-system.git (fetch)\norigin  https://github.com/Itzx-kush/Student-information-management-system.git (push)",
            "explanation": "If origin is missing, it is configured using 'git remote add origin <URL>'."
        },
        {
            "step": 8,
            "title": "Push Changes to Remote GitHub Repository",
            "command": "git push -u origin main",
            "purpose": "Transfers committed local commits to GitHub and sets up upstream branch tracking.",
            "output": "Enumerating objects: 15, done.\nCounting objects: 100% (15/15), done.\nWriting objects: 100% (15/15), 18.42 KiB | 2.30 MiB/s, done.\nTo https://github.com/Itzx-kush/Student-information-management-system.git\n * [new branch]      main -> main\nBranch 'main' set up to track remote branch 'main' from 'origin'.",
            "explanation": "Transfers the commit tree over HTTPS to GitHub, publishing the code."
        },
        {
            "step": 9,
            "title": "Synchronize Changes from Remote",
            "command": "git pull origin main",
            "purpose": "Fetches and integrates remote commits from GitHub into the local active branch.",
            "output": "From https://github.com/Itzx-kush/Student-information-management-system\n * branch            main       -> FETCH_HEAD\nAlready up to date.",
            "explanation": "Ensures the developer has the latest updates made by collaborators before starting new work."
        },
        {
            "step": 10,
            "title": "Review Commit Log History",
            "command": "git log --oneline",
            "purpose": "Displays a concise single-line view of recent commits in reverse chronological order.",
            "output": "a1b2c3d (HEAD -> main, origin/main) Add student management system\n3440577 Initial commit",
            "explanation": "Validates that the commit history matches expectations across local and remote pointers."
        }
    ]
    return render_template('git/github_workflow.html', steps=steps)


@git_bp.route('/collaboration')
def collaboration():
    """Module E (Question C): Complete Git Workflow and Collaborative Development."""
    checklist_status = session.get('git_checklist', {})
    completed_count = sum(1 for item in CHECKLIST_ITEMS if checklist_status.get(item['id']))
    progress_percentage = int((completed_count / len(CHECKLIST_ITEMS)) * 100) if CHECKLIST_ITEMS else 0

    return render_template(
        'git/collaboration.html',
        checklist_items=CHECKLIST_ITEMS,
        checklist_status=checklist_status,
        completed_count=completed_count,
        total_items=len(CHECKLIST_ITEMS),
        progress_percentage=progress_percentage
    )


@git_bp.route('/checklist/toggle', methods=['POST'])
def toggle_checklist():
    """Toggle a concept item in the student Git checklist."""
    item_id = request.form.get('item_id', '').strip()
    status = request.form.get('status') == 'true'

    if 'git_checklist' not in session:
        session['git_checklist'] = {}

    checklist = dict(session['git_checklist'])
    checklist[item_id] = status
    session['git_checklist'] = checklist

    completed_count = sum(1 for item in CHECKLIST_ITEMS if checklist.get(item['id']))
    progress_percentage = int((completed_count / len(CHECKLIST_ITEMS)) * 100) if CHECKLIST_ITEMS else 0

    return jsonify({
        'success': True,
        'item_id': item_id,
        'status': status,
        'completed_count': completed_count,
        'total_items': len(CHECKLIST_ITEMS),
        'progress_percentage': progress_percentage
    })
