# Project Description
Generate a full Python CLI application called "LocalMeetingTranscriber" that processes iPhone .m4a recordings into Word (.docx) meeting transcripts.

The program must:
1. Read all .m4a files from a folder called "input_audio/".
2. Convert each .m4a into a 16kHz mono .wav using ffmpeg.
3. Run whisper.cpp on the .wav file with a large-v3 Q5_0 model to produce a raw transcript with timestamps.
4. Offer a CLI menu to select one of four modes:
   - 1. Full transcript (with timestamps)
   - 2. Clean transcript (without timestamps)
   - 3. Polished transcript (using local LLM for better formatting)
   - 4. Polished transcript with appendix including raw timestamp output
5. Generate Word documents (.docx) using python-docx with correct file naming:
   - Format: YYYY-MM-DD_<meeting-name>_<mode>.docx
6. Clean up intermediate files and organize output into appropriate folders.
7. Provide clear comments in English.

The repository must include:
- A main.py that orchestrates the workflow.
- A core/ folder with modules:
   - converter.py (ffmpeg conversion)
   - transcriber.py (whisper.cpp invocation)
   - postprocess.py (cleaning and timestamp removal)
   - exporter.py (docx generation)
   - llm_polisher.py (optional LLM-based polish)
- A config/ settings.yaml for adjustable parameters such as model path and default settings.
- A README.md describing how to install and run the program on an Intel macOS machine.
- Use python 3.11 compatible syntax.

Expectations:
- The CLI needs a clear, user-friendly menu with input validation.
- All external calls (ffmpeg, whisper.cpp, optional LLM) must handle errors gracefully.
- The transcript must retain proper encoding and handle non-ASCII characters.
- Use structured code with functions and classes where appropriate.

# Output
Return a zip-ready tree with complete files and working code.

Quality Requirements:
- Functions should be short and modular.
- Include docstrings and type hints.
- Include error handling for common edge cases.
- Provide usage examples in the README.
- Avoid 3rd party services or APIs outside local dependencies.

Also include a tests/ folder with PyTest tests covering each core module edge cases.