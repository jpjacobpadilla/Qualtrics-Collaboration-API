<p align="center">
    <img src="logo.png" width="250px">
</p>

<h2 align="center">An easy way for NYU students to collaborate on Qualtrics surveys</h2>

This Python package provides a streamlined solution for NYU students to collaborate on Qualtrics surveys. It simplifies the process of adding collaborators to a survey and managing access.

<br>

Here's a quick guide on how to use this package:

1. **Import the Client**:
   Begin by importing the `CollaborationClient` class from the package.

   ```python
   from qualtrics_collaboration import CollaborationClient
   ```

2. **Create a Client Instance**:
   Create an instance of `CollaborationClient`.

   ```python
   client = CollaborationClient()
   ```

3. **Login**:
   Log in to your Qualtrics account through the client.

   ```python
   client.login()
   ```

4. **Add a Collaborator**:
   Add a collaborator to your survey by providing the survey ID and the collaborator's username or email.

   ```python
   client.add_collaborator(survey_id='SV_SURVEY_ID', collaboration_username='USERNAME/EMAIL')
   ```

5. **Enter Collaboration Code**:
   If you have a collaboration code for an existing survey, enter it to join the survey.

   ```python
   client.enter_collaboration_code(code='COLLABORATION_CODE')
   ```
