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


def retrieve_code(repo, commit_hash_or_branch):
    try:
        # Assuming you want to retrieve code from a specific commit or branch
        repo.git.checkout(commit_hash_or_branch)
        code = repo.git.show("--pretty=format:", "--name-only")
        return code
    except Exception as e:
        raise ValueError(f"Failed to retrieve code: {str(e)}")
