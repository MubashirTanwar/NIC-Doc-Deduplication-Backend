from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework.exceptions import Throttled

class CustomUserRateThrottle(UserRateThrottle):
    def wait(self):
        duration = super().wait()
        if duration:
            raise Throttled(detail={
                'error': 'Rate limit exceeded.',
                'details': f'You have exceeded the rate limit of {self.num_requests} requests per {self.duration} seconds.', 
                'code': 429   
            })
        return duration