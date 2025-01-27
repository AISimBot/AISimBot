# AI Sim Bot

Education through AI-Powered Simulations

## Overview

AI SimBot is a cutting-edge tool designed to enhance clinical educational experiences through realistic communication simulations. Initially created for prelicensure nursing students at Northeastern University to practice administering the CRAFFT, a screening tool for identifying substance use among youth, it now offers customizable settings for a wide range of educational and professional contexts focused on role-playing and communication skills.

### Key Features

- Customizable Scenarios: Adaptable for various disciplines and learning objectives, including:
  - Communication skills
  - Interviewing techniques
  - Role-playing scenarios
  - Verbal interaction practice

- Flexible Role-Playing: Supports diverse applications, such as:
  - Scenario-based learning in healthcare, social work, law, and more
  - Educational role-plays (e.g., teacher-student, counselor-client, or peer mediation)
  - Professional training (e.g., job interviews, customer service, or team communication)

- Real-Time Feedback: Provides instant evaluations and feedback to refine user skills effectively.

- Transcript Downloads: Allows users to save a complete transcript of the interaction as a Word document for review, reflection, or documentation.

### Benefits

- Accessibility: Practice anytime, anywhere, without the need for live actors or physical spaces.
- Scalability: Support diverse learners and training needs.
- Flexibility: Customize scenarios to meet specific educational or professional goals.
- Cost-Effectiveness: Replace costly and time-intensive role-playing exercises with a digital solution.

## Demo

https://github.com/user-attachments/assets/ad79cd24-13ff-492a-9de3-059b10e470fe

## Setup

In order to launch this app, you need to configure and set up the following three services:

1. [Create an OpenAI account](https://platform.openai.com/api-keys).  
   - Purpose: Provides the AI capabilities for the app, including managing conversations, converting speech to text, and generating spoken responses.
   - [Generate an API key](https://platform.openai.com/api-keys).  
   - Write down your key, as it will not be shown again.  
   - You can delete and create a new key if needed.  
   - [Purchase credits](https://help.openai.com/en/articles/8264644-how-can-i-set-up-prepaid-billing) for API use. It may takes a few hours for API to be active.

2. [Create a GitHub account](https://github.com/signup).  
   - Purpose: Organizes and stores the app's code, making it easy to update and manage.
   - [Click here and fork this project](https://github.com/AISimBot/AISimBot/fork).  
   - Name your fork and click **Create fork**.  
   - Save the URL for your forked repository.  

3. [Create a Streamlit account](https://streamlit.app/).  
   - Purpose: Hosts the app on a server and makes it accessible to users through a browser.
   - Click **Create an app**.  
   - Select **Deploy from repo**.  
   - Enter the URL of your forked repository.  
   - Provide a unique and memorable URL for your app.  
   - Choose **Advanced settings**, and under **Secrets**, add your OpenAI API key and app password in the following format:  

   ```toml
   OPENAI_API_KEY = "your_openai_api_key"
   password = "your_app_password"
   ```

   - Click **Save** and then **Deploy**.

> **Note:** Secrets may take a few minutes to propagate. If you see an error about a missing key, wait a few minutes and then [reboot](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app) your app by going to **Manage app** (in the lower-right corner) and clicking the overflow menu icon and then reboot.

If the issue persists, confirm that the key appears under **App settings > Secrets**.

Once set up correctly, you’ll see the app interface.

### Testing Your App

1. Click **Share** to get your app link.  
2. Open the link in a private browsing window or log out of Streamlit.  
   - **Shortcut keys:**  
     - Chrome, Safari, Edge: `Ctrl-Shift-N` (Windows) or `Command-Shift-N` (Mac).  
     - Firefox: `Ctrl-Shift-P` (Windows) or `Command-Shift-P` (Mac).

### Customize

1. Go to your forked repository on GitHub.  
2. Navigate to the `settings.toml` file and click **Edit file**.  
3. Update the file content as needed and click **Commit changes**.  
   - Add a short, descriptive title and summary for your changes.  

The `settings.toml` file uses [TOML](https://toml.io/en/) format. For multiline fields, enclose text in `'''`. You can also use [Markdown](https://www.markdownguide.org/getting-started/) for formatting.

- **Intro**: Displays before users start chatting.  
- **Sidebar**: Contains fields that appear on the app’s sidebar.  

To update avatars, replace the relevant files in the `assets` folder.

To customize basic theme settings such as colors and fonts, edit the .streamlit/config.toml file. For advanced styling, modify the style.css file.

**IMPORTANT**: After commit changes, you need to [reboot](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app) your app by going to **Manage app** (in the lower-right corner) and clicking the overflow menu icon and then reboot.

### Importance of Prompt

The content in prompt.txt is the most critical component of the AI SimBot, as it directly shapes the quality and relevance of the user experience.

1. Be Clear and Specific: Clearly define the AI's role, purpose, and behavior to minimize ambiguity.  
   - Example: *"You are Jordan, a 17-year-old non-binary high school student visiting a pediatric office for a routine physical. Speak naturally and respond based on the provided patient background."*

2. Provide Sufficient Context: Offer background details to help the AI generate relevant and realistic responses.  
   - Example: *"Jordan has started using substances occasionally to cope with academic and social pressures and feels nervous about the CRAFFT screening due to concerns about judgment and confidentiality."*

3. Guide Behavior with Clear Instructions: Specify how the AI should behave in different scenarios.  
   - Example: *"Begin the conversation feeling nervous and guarded. Gradually open up if the nurse is empathetic and supportive. If the nurse is judgmental, withdraw emotionally and respond defensively."*

4. Use Step-by-Step Instructions: Break down tasks into smaller, manageable steps for the AI to follow.  
   - Example: *"Start the conversation with an introduction. Respond to the nurse’s questions using short, vague answers at first. Adjust your emotional openness based on the nurse’s tone."*

5. Define Boundaries: Set clear limits on what the AI should avoid or omit.  
   - Example: *"Do not ask any questions. Do not mention the CRAFFT manual. If the nurse asks something outside your scope, respond with, 'I’m not aware of that.'"*

6. Incorporate Examples for Clarity: Provide sample responses to illustrate the desired behavior.  
   - Example: *"When nervous, say things like, 'It’s not a big deal,' or 'I only do it sometimes.' If the nurse is empathetic, you might say, 'Sometimes I just need an escape.' If they are judgmental, respond with, 'Can we stop now?' or 'I think I’m done here.'"*

7. Encourage Realism and Consistency: Make the AI’s responses more engaging and authentic.  
   - Example: *"Use casual Gen Z slang like 'low-key,' 'vibe,' or 'no cap' to sound like a typical teenager. Reflect Jordan’s emotions and background in every response."*

8. Iterate and Test for Improvements: Continuously test and refine the prompt to ensure it delivers the desired outcomes.  
   - Insight: Tuning the prompt for CRAFFT practice required multiple rounds of iterative testing with graduate-level nursing students to optimize the SimBot's performance.

For more information, check out [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) by OpenAI.

## Technologies Used

- [Streamlit](https://streamlit.io/): For building an interactive user interface.
- OpenAI API: For text generation through GPT-4o (large language model), text to speech, and speech to text ((Whisper.)

## Potential Use Cases

The AI SimBot’s versatility makes it valuable for:

- Healthcare and Counseling Training: Practice patient-provider communication and diagnostic skills.
- Youth Development Programs: Role-play scenarios like peer mediation, bullying intervention, or leadership development.
- Cross-Cultural Communication: Improve interactions in diverse cultural contexts.
- Education and Teaching: Prepare for classroom scenarios, student counseling.
- Language Learning: Build conversational fluency and cultural competence.
- Legal Practice: Practice depositions, client consultations, or courtroom questioning.
- Law Enforcement Training: Simulate suspect or witness interviews to sharpen investigative skills.
- Sales and Marketing: Enhance client interaction techniques for persuasion and negotiation.
- Corporate Training: Improve job interview skills, customer service, conflict resolution, and team communication.

## Contributers

* Yash Pankhania
* Tiffany Kim
