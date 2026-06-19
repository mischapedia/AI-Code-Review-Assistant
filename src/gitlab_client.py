import gitlab
import base64

class GitLabClient:
    def __init__(self, url: str, token: str):
        self.gl = gitlab.Gitlab(url, private_token=token)

    def get_mr_metadata(self, project_id: str | int, mr_iid: int) -> dict:
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        return {
            "title": mr.title,
            "description": mr.description,
            "author": mr.author.get('username') if mr.author else "Unbekannt"
        }

    def get_mr_diffs(self, project_id: str | int, mr_iid: int) -> list:
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        return mr.changes()['changes']
    
    def get_file_content(self, project_id: str | int, file_path: str, ref: str) -> str:
        project = self.gl.projects.get(project_id)
        file = project.files.get(file_path=file_path, ref=ref)
        return base64.b64decode(file.content).decode('utf-8')

    def post_comment(self, project_id: str | int, mr_iid: int, comment: str):
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        mr.notes.create({'body': comment})