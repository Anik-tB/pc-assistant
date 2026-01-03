"""
Voice Controller Module
Speech recognition and text-to-speech functionality
"""

import speech_recognition as sr
import pyttsx3
import threading
from typing import Optional, Callable
import queue


class VoiceController:
    """Voice command controller with speech recognition and TTS"""

    def __init__(self, wake_word: str = "hey assistant"):
        """Initialize voice controller"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.wake_word = wake_word.lower()

        # Configure TTS
        self.tts_engine.setProperty('rate', 150)  # Speed
        self.tts_engine.setProperty('volume', 0.9)  # Volume

        # Voice settings
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)  # Use first voice

        # State
        self.listening = False
        self.command_queue = queue.Queue()

        # Calibrate for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def speak(self, text: str):
        """Convert text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """
        Listen for a single command

        Args:
            timeout: Maximum time to wait for speech

        Returns:
            Recognized text or None
        """
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            try:
                text = self.recognizer.recognize_google(audio)
                print(f"📝 Recognized: {text}")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Recognition service error: {e}")
                return None

        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return None

    def listen_for_wake_word(self, callback: Optional[Callable] = None):
        """
        Continuously listen for wake word

        Args:
            callback: Function to call when wake word detected
        """
        self.listening = True

        def listen_loop():
            while self.listening:
                text = self.listen_once(timeout=3)

                if text and self.wake_word in text.lower():
                    print(f"✅ Wake word detected!")
                    self.speak("Yes, I'm listening")

                    # Listen for actual command
                    command = self.listen_once(timeout=5)

                    if command:
                        if callback:
                            callback(command)
                        else:
                            self.command_queue.put(command)

        # Start listening in background thread
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()

    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False

    def get_command(self, block: bool = True, timeout: Optional[float] = None) -> Optional[str]:
        """
        Get command from queue

        Args:
            block: Whether to block until command available
            timeout: Maximum time to wait

        Returns:
            Command text or None
        """
        try:
            return self.command_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def test_microphone(self) -> bool:
        """Test if microphone is working"""
        try:
            with self.microphone as source:
                print("🎤 Testing microphone... Say something!")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Microphone working! Heard: {text}")
                return True
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False

    def list_microphones(self):
        """List available microphones"""
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {index}: {name}")


# Example usage
if __name__ == "__main__":
    voice = VoiceController()

    # Test microphone
    voice.test_microphone()

    # List available microphones
    voice.list_microphones()

    # Test TTS
    voice.speak("Voice controller initialized successfully")

    # Listen for a single command
    print("\nSay a command:")
    command = voice.listen_once()
    if command:
        voice.speak(f"You said: {command}")
