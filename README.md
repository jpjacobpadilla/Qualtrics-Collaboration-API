## NYU student collaboration on Qualtrics surveys made easy

**Example Usage:**
```python
from qualtrics_collaboration import CollaborationClient

client = CollaborationClient()
client.login()
client.add_collaborator(survey_id='SV_SURVEY_ID', collaboration_username='USERNAME/EMAIL')
client.enter_collaboration_code(code='COLLABORATION_CODE')
```