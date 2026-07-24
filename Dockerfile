# Containerised deterministic reproduction. Recomputes every reference value with
# two independent implementations, regenerates the task-level statistics from the
# archived run records, and redraws the three figures. It calls no model.
# Re-running the experiment itself needs paid model interfaces and is out of scope
# here; the archived run records are included.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mount the repository to collect the outputs:
#   docker run --rm -v "$PWD:/work" spec-repro
CMD ["make", "reproduce"]
