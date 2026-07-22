# Containerised deterministic reproduction. Recomputes every reference value with two
# independent implementations, regenerates the task-level statistics from the archived
# run records, redraws both figures, and rebuilds the three Word documents. It calls no
# model. Re-running the experiment itself needs paid model interfaces and is out of
# scope here; the archived run records are included.
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
