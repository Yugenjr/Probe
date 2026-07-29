import subprocess
from typing import Dict, Any, List

class GitChangeAgent:
    def __init__(self):
        pass

    async def fetch(self, repo_path: str = None) -> List[Dict[str, Any]]:
        # Fetch real git commits from local repo
        try:
            output = subprocess.check_output(
                ["git", "log", "-n", "5", "--name-status", "--pretty=format:COMMIT|%H|%an|%s"],
                cwd=repo_path or ".",
                text=True,
                encoding="utf-8"
            )
            raw_commits = []
            current_commit = None
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("COMMIT|"):
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        current_commit = {
                            "commit_hash": parts[1],
                            "committer": parts[2],
                            "msg": parts[3],
                            "files": []
                        }
                        raw_commits.append(current_commit)
                elif current_commit is not None:
                    # files lines look like "M\tpath/to/file" or just "path/to/file"
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        current_commit["files"].append(parts[1])
                    else:
                        current_commit["files"].append(line)
            return raw_commits
        except Exception as e:
            print(f"Error fetching git changes: {e}")
            return []

    def normalize(self, raw_commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        normalized = []
        for commit in raw_commits:
            normalized.append({
                "hash": commit.get("commit_hash", ""),
                "author": commit.get("committer", ""),
                "message": commit.get("msg", ""),
                "files_changed": commit.get("files", [])
            })
        return {"commits": normalized}

    def validate(self, normalized_data: Dict[str, Any]) -> bool:
        if "commits" not in normalized_data:
            return False
        for commit in normalized_data["commits"]:
            if not all(k in commit for k in ["hash", "author", "message", "files_changed"]):
                return False
        return True
