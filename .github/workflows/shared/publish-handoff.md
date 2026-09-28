---
safe-outputs:
  jobs:
    publish-handoff:
      description: Publish one versioned, validated agent handoff as a workflow artifact
      runs-on: ubuntu-latest
      output: Validated handoff artifact published
      permissions:
        contents: read
        actions: read
      inputs:
        payload:
          description: Complete handoff object serialized as JSON
          required: true
          type: string
      steps:
        - name: Checkout
          uses: actions/checkout@v7

        - name: Extract and validate handoff
          id: handoff
          run: |
            set -euo pipefail
            python3 tests/policy/extract_handoff.py \
              --agent-output "$GH_AW_AGENT_OUTPUT" \
              --output build/handoff/handoff.json
            echo "handoff_type=$(jq -r .handoff_type build/handoff/handoff.json)" \
              >> "$GITHUB_OUTPUT"

        - name: Correlate diagnosis with source CI run
          if: github.event_name == 'workflow_run' && steps.handoff.outputs.handoff_type == 'diagnosis'
          env:
            SOURCE_REPOSITORY: ${{ github.repository }}
            SOURCE_RUN_ID: ${{ github.event.workflow_run.id }}
            SOURCE_RUN_URL: ${{ github.event.workflow_run.html_url }}
            SOURCE_SHA: ${{ github.event.workflow_run.head_sha }}
          run: |
            set -euo pipefail
            python3 tests/policy/validate_handoff.py \
              --input build/handoff/handoff.json \
              --expected-type diagnosis \
              --source-repository "$SOURCE_REPOSITORY" \
              --source-run-id "$SOURCE_RUN_ID" \
              --source-run-url "$SOURCE_RUN_URL" \
              --source-sha "$SOURCE_SHA"

        - name: Download predecessor handoff
          if: github.event_name == 'workflow_run' && steps.handoff.outputs.handoff_type != 'diagnosis'
          uses: actions/download-artifact@v8
          with:
            name: agent-handoff
            path: build/upstream
            github-token: ${{ github.token }}
            run-id: ${{ github.event.workflow_run.id }}

        - name: Correlate chained handoff provenance
          if: github.event_name == 'workflow_run' && steps.handoff.outputs.handoff_type != 'diagnosis'
          env:
            PREDECESSOR_RUN_ID: ${{ github.event.workflow_run.id }}
          run: |
            set -euo pipefail
            python3 tests/policy/validate_handoff_chain.py \
              --current build/handoff/handoff.json \
              --upstream build/upstream/handoff.json \
              --predecessor-run-id "$PREDECESSOR_RUN_ID"

        - name: Upload validated handoff
          uses: actions/upload-artifact@v7
          with:
            name: agent-handoff
            path: build/handoff/handoff.json
            if-no-files-found: error
            retention-days: 14
---
