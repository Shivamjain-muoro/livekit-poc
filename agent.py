from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from prompts import AGENT_INSTRUCTION, INTERVIEWER_INSTRUCTION, SESSION_INSTRUCTION
from tools import (
    create_interview_session, upload_resume_and_analyze, generate_tailored_questions,
    start_interview, record_answer, evaluate_interview, get_interview_status,
    pause_resume_interview, get_weather, search_web, send_email
)
load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=SESSION_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
            voice="Aoede",
            temperature=0.8,
        ),
            tools=[
                create_interview_session,
                upload_resume_and_analyze,
                generate_tailored_questions,
                start_interview,
                record_answer,
                evaluate_interview,
                get_interview_status,
                pause_resume_interview,
                get_weather,
                search_web,
                send_email
            ],

        )
        


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Example: frame is a NumPy array from your video stream
    # You need to obtain a frame from your video stream here.
    # For demonstration, we'll set frame = None. Replace this with actual frame acquisition logic.
    # frame = None  # TODO: Replace with actual frame from video stream
    # result = await detect_face_motion(session.context, frame)
    # if session.context.state.get("interview_paused"):
    #     await session.generate_reply(instructions=result)
    #     # Pause interview as needed
    # else:
    #     # Continue interview

    await session.generate_reply(
        instructions="Welcome to the AI Interview System! I'm Friday, your AI interviewer. I'll guide you through a comprehensive interview process. Let's start by creating your interview session. Please provide your name, email, job role you're applying for, and your experience level."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))