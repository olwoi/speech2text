from time import time
import logging
from requests import post
from os import path
from platform import system
from subprocess import run, CalledProcessError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SERVER_URL = "http://localhost:8006/whisper/"


def get_path(dir_name, file_name):
    return path.join(path.dirname(path.abspath(__file__)), dir_name, file_name)


def log_response(response, total):
    whisper = round(float(response.headers.get("Time-Whisper")), 3)
    tts = round(float(response.headers.get("Time-TTS")), 3)
    logging.info(f"Total delay of {total}s: Whisper took {whisper}s and TTS took {tts}s")


def play_audio(audio_path):
    """
    This function is supposed to play audio given a path, but has only been tested on Raspbian, Darwin and Windows.
    """
    if audio_path is None:
        logging.error("Error in play_audio: No audio path provided")

    os_name = system()
    if os_name == "Linux":
        try:
            run(["mpg321", "-q", audio_path], check=True)
        except CalledProcessError as e:
            logging.error(f"Error playing audio on Linux: {e}")
    elif os_name == "Windows":
        try:
            run(["cmd.exe", "/c", "start", "/wait", audio_path], check=True)
        except CalledProcessError as e:
            logging.error(f"Error playing out on Windows: {e}")
    elif os_name == "Darwin":
        try:
            run(['afplay', audio_path], check=True)
        except CalledProcessError as e:
            logging.error(f"Error playing audio on macOS: {e}")
    else:
        raise OSError(f"Unsupported operation system: {os_name}")


def remote_whisper(input_file_path):
    """
    sends local audio file to server, saves response and returns its location.
    """
    try:
        with open(input_file_path, "rb") as file:
            files = {"file": file}
            current_time = time()
            response = post(SERVER_URL, files=files)
            total_time = time() - current_time
        if response.status_code == 200:
            language = response.headers.get("X-Language")
            log_response(response, round(total_time, 3))
            output_file_path = get_path("audio_files", "output.mp3")
            print("Pfad:" + output_file_path)
            with open(output_file_path, "wb") as f:
                f.write(response.content)
            return output_file_path, language
        else:
            logging.error(f"Server responded with status code: {response.status_code}")
            return None, None
    except Exception as e:
        logging.error(f"Error prompting server: {e}")
        return None, None


if __name__ == "__main__":
    # currently just takes a local input.mp3 and plays response (output.mp3)
    file_path, language = remote_whisper(get_path("audio_files", "input.mp3"))
    play_audio(file_path)
