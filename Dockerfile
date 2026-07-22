# Containerised deterministic reproduction: regenerates all statistics, figures,
# and the manuscript + Supporting Information documents from results_v2.json.
# (Re-running the LLM-agent experiments is out of scope — it needs an agent harness;
#  the archival scalar and report run sets are included.)
FROM python:3.12-slim

# Node.js for the docx build scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
        nodejs npm make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY manuscript/package.json manuscript/package.json
RUN cd manuscript && npm install

COPY . .

# Default: reproduce the deterministic layer. Mount the repo to collect outputs:
#   docker run --rm -v "$PWD:/work" mee-repro
CMD ["make", "reproduce"]
