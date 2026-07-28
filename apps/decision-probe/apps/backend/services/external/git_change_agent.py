from typing import Dict, Any, List

class GitChangeAgent:
    def __init__(self):
        pass

    async def fetch(self, repo_path: str = None) -> List[Dict[str, Any]]:
        # Simulated Git commit details (e.g. GitHub/Git CLI local inspection)
        raw_commits = [
            {
                "commit_hash": "a4f8d29b",
                "committer": "alex.engineer@company.com",
                "msg": "feat: optimize database connection pools settings & reduce timeout thresholds",
                "files": [
                    "apps/payments/src/config/database.ts",
                    "apps/payments/package.json"
                ]
            }
        ]
        return raw_commits

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
