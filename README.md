# Rachel for Podcasters

Rachel is an AI transcription tool for analyzing spoken content like podcasts in real time. Imagine the AI version of "Jamie" from *The Joe Rogan Experience*: a live assistant that listens in, flags interesting or controversial claims, and looks them up for you automatically.

The UI displays a real-time transcript of the conversation. Flagged words and phrases are highlighted and enriched with additional context and detail, providing nuance and accuracy to what was said.

This was initially a personal project (the name 'Rachel' is an homage to our own _human_ podcast assistant, Rachel — _“Hey Rachel, can you look that up for me…”_) but as it evolved, it started feeling really useful: having real-time analysis of all the content you listen to — for fact-checking, for learning, or even simply better comprehension on new topics. So, I decided to open it up in case anyone else wanted to see this built out to more use cases; i'll clean it up as I go.

#### For OSS community:

The codebase is still making its way from a personal project to an "oss project" and still needs some clean-up and a few basics (eg, tests). I intend to build those out eventaully (_especially if there is interest_) as well as these:
  - Support for multiple, simultaneous deep LLM clients. The idea being that by seeing both side-by-side you could get possible signals of bias from specific LLMs.
  - Chrome plugin. This will be a larger effort, but the idea is real-time fact-checking and contextual prompts for any spoken content (podcasts, shows, etc.) on the web.
  - Training/adding adapters (fine-tuning) for the shallow models. Once I can get one with proper licensing, I will add it to the repo so it works out of the box.

So feel free to fork or clone and I will generally engage with PR's in those directions.

---

[Installation](docs/install.md)

[Configure LAN setup](docs/lan_setup.md)

[Getting Started](docs/getting_started.md)

[How It Works](docs/how_it_works.md)

[config.yaml Reference](docs/config.md)

--- 

## ✅ What Works Out Of Box
The app comes with a known-good setup for CUDA enabled machines in the `config.yaml`. After you've provided your API keys:
- All ports, model settings, and audio parameters are ready to go
- Models will auto-download on first run
- Transcripts are saved in `src/transcripts/transcript.json`

## ⚙️ What’s Configurable
It was built to be modular meaning you can easily customize:
- Which models are used at each stage
- Streaming and audio parameters (bitrate, overlap, chunking)
- Frontend behavior and appearance

## 🖥️ Overview:

#### Server (PC with GPU):
The app was built to be run locally on a desktop (or some other machine with GPU) connected into your live mic feed or audio interface. A reasonable PC/GPU should suffice here however, the app will be running numerous models locally which can overpower machines without decent GPU acceleration.

#### Client (viewers on laptops):
Once the server is running, everyone else in the room can just open a web browser and connect over local Wi-Fi. There is nothing to install on those devices. Just open the link and watch the interactive transcript populate in real time.

#### What it does:
As the app runs, it automatically listens for any factual claims or otherwise interesting details. When it detects something, it reaches out to a deeper model (eg, gpt-4) for rich/relevant context; pulling out the key phrases, scoring them for relevance and severity, and updating showing all this in (near) real time.

Now, of course, an app could just stream the entire transcription through the deep/paid models and always get the best transcription but that would be wasteful and expensive. The idea with Rachel is about having that deeper (paid) AI enrichment but only when its needed. 

It does this by using shallower LLM's locally (ie, free) to determine if the content is worth a deeper investigation before sending requests to the paid models. In technical terms, this is often referred to a Cascaded Inference pipeline; with other cool things like semantic filtering to that same end.

tldr; You can tune the prompts, experiment with different LLM's or even fine-tune your own LLM to get the best output for your subject domain. 
