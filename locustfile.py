import random
from locust import HttpUser, task, between

class IslamicPlatformUser(HttpUser):
    # Simulates a user waiting 1 to 5 seconds between actions
    wait_time = between(1, 5)

    

    @task(1)
    def search_lessons(self):
        """Simulates a user typing in the search bar"""
        # Adjust the query parameter 'q' or 'search' to match your backend
        self.client.get("/videos/1/play")

    
    @task(1)
    def simulate_play_audio(self):
        """Simulates the API call made when '🎵 Audio' is clicked"""
        video_id = random.randint(1, 20)
        self.client.get(f"/videos/{video_id}/play")