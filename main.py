from datetime import datetime

from cpmpy import Model, intvar
from pydantic import BaseModel

from fastapi import FastAPI, status, HTTPException


# Base model for request body in POST model
class Meeting(BaseModel):
    start_time: datetime
    end_time: datetime
    seats_required: int


app = FastAPI()

# List of all meeting
all_meeting = []

# Total number of seats in the conference room.
all_seat_room = 10


# Function for checking the meeting info is correct
def check_meeting_details(start_time, end_time, seats_required):
    # Create model
    model = Model()

    start_time = intvar(lb=int(start_time.timestamp()), ub=int(start_time.timestamp()))
    end_time = intvar(lb=int(end_time.timestamp()), ub=int(end_time.timestamp()))

    for meeting in all_meeting:
        model += (start_time >= int(meeting.end_time.timestamp())) | (end_time <= int(meeting.start_time.timestamp()))

    # Check if time is available
    if model.solve():
        model += (all_seat_room >= seats_required)

        # Check if required seat is less than max number of seat

        if model.solve():
            return 1
        return -1
    return 0


# Get all meeting
@app.get('/meetings')
def meetings():
    return all_meeting


@app.post('/schedule_meeting', status_code=status.HTTP_200_OK)
def schedule_meeting(meet: Meeting):
    # Check if required seat is more than 1
    if meet.seats_required >= 1:

        # Check if starting time is earlier than ending time
        if meet.start_time.timestamp() <= meet.end_time.timestamp():

            if check_meeting_details(meet.start_time, meet.end_time, meet.seats_required) == 1:

                all_meeting.append(meet)
                return meet

            elif check_meeting_details(meet.start_time, meet.end_time, meet.seats_required) == -1:

                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='required seats is more than max number of seat in the conference room.')
            else:

                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='the time has already Reserved ')
        else:

            raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                                detail='starting time must be earlier than ending time')
    else:

        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                            detail='required seats must be at least 1')
