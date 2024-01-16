from crewai import Crew
from textwrap import dedent
from trip_agents import TripAgents
from trip_tasks import TripTasks
import streamlit as st
import datetime

st.set_page_config(page_icon="✈️", layout="wide")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

class TripCrew:

  def __init__(self, origin, cities, date_range, interests):
    self.cities = cities
    self.origin = origin
    self.interests = interests
    self.date_range = date_range

  def run(self, update_callback=None):
    agents = TripAgents()
    tasks = TripTasks()
    
    city_selector_agent = agents.city_selection_agent()
    local_expert_agent = agents.local_expert()
    travel_concierge_agent = agents.travel_concierge()
  
    if update_callback:
            update_callback("Initializing trip planning process...")
    identify_task = tasks.identify_task(
      city_selector_agent,
      self.origin,
      self.cities,
      self.interests,
      self.date_range
    )

    if update_callback:
            update_callback("Agent is gathering tasks...")
    gather_task = tasks.gather_task(
      local_expert_agent,
      self.origin,
      self.interests,
      self.date_range
    )

    plan_task = tasks.plan_task(
      travel_concierge_agent, 
      self.origin,
      self.interests,
      self.date_range
    )

    crew = Crew(
      agents=[
        city_selector_agent, local_expert_agent, travel_concierge_agent
      ],
      tasks=[identify_task, gather_task, plan_task],
      verbose=True
    )

    result = crew.kickoff()

    if update_callback:
            update_callback("Agent is finalizing tasks...")

    return result

if __name__ == "__main__":
  icon("🏖️ VacAIgent")

  st.info("**Let AI agents plan your next vacation...**")
  
  import datetime

  today = datetime.datetime.now().date() 
  next_year = today.year + 1
  jan_16_next_year = datetime.date(next_year, 1, 10)

  with st.sidebar:
    st.header("👇 Enter your trip details")
    with st.form("my_form"):
      location = st.text_input("Where are you currently located?", placeholder="San Mateo, CA")
      cities = st.text_input("City and country are you interested in vacationing at?", placeholder="Bali, Indonesia")
      date_range = st.date_input(
        "Date range you are interested in traveling?",
        min_value=today, 
        value=(today, jan_16_next_year + datetime.timedelta(days=6)), 
        format="MM/DD/YYYY",
      )
      interests = st.text_area("High level interests and hobbies or extra details about your trip?", placeholder="2 adults who love swimming, dancing, hiking, and eating")

      submitted = st.form_submit_button("Submit")
    
    st.divider()
    
    # Credits to joaomdmoura/CrewAI for the code: https://github.com/joaomdmoura/crewAI
    st.sidebar.markdown(
        """
        Credits to [**@joaomdmoura**](https://twitter.com/joaomdmoura) 
        for creating **crewAI** 🚀
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.info("Click the logo to visit GitHub repo", icon="👇")
    st.sidebar.markdown(
        """
        <a href="https://github.com/joaomdmoura/crewAI" target="_blank">
            <img src="https://raw.githubusercontent.com/joaomdmoura/crewAI/main/docs/crewai_logo.png" alt="CrewAI Logo" style="width:100px;"/>
        </a>
        """,
        unsafe_allow_html=True
    )


def update_status(status_container, message):
    """Callback function for updates"""
    status_container.write(message)

if submitted:
    with st.status("**Grab a coffee or go for a ~20 minute walk, processing your trip plan...**", expanded=True) as status:
      trip_crew = TripCrew(location, cities, date_range, interests)
      result = trip_crew.run(update_callback=lambda msg: update_status(status, msg))
      # Update the status container to indicate completion and time taken
      status.update(label="✅ Trip Plan Ready!", state="complete", expanded=False)
  
    st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
    st.markdown(result)