import git

def clone_repo(repo_url, temp_dir, access_token):
    try:
        # Modify the URL to include the access token
        if access_token:
            repo_url = repo_url.replace('https://', f'https://{access_token}@')
        repo = git.Repo.clone_from(repo_url, temp_dir)
        return repo
    except Exception as e:
        raise ValueError(f"Failed to clone repository: {str(e)}")


def retrieve_code(repo, branch_name):
    try:
        print(f"Attempting to checkout branch: {branch_name}")  # Diagnostic print statement
        repo.git.fetch()  # Fetch the latest updates from the remote
        repo.git.checkout(branch_name)
        code = repo.git.show("--pretty=format:", "--name-only")
        return code
    except Exception as e:
        raise ValueError(f"Failed to retrieve code: {str(e)}")

