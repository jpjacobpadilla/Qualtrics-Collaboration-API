# An easy way for NYU students to collaborate on Qualtrics surveys.

Example Usage:
```python
client = CollaborationClient()
client.login()
client.add_collaborator(survey_id='SV_SURVEY_ID', collaboration_username='USERNAME/EMAIL')
client.enter_collaboration_code(code='COLLABORATION_CODE')
```