# Build only after verifying d085-candidate == sha256:19af4754... (D085 lock).
FROM local/voicebox:d085-candidate
USER 999:999
# Image-owned cache only. No bind-mount permissions or production data are changed.
COPY --chown=999:999 home/ /home/voicebox/
COPY --chmod=0755 entrypoint-uid999.sh /usr/local/bin/entrypoint-uid999.sh
ENTRYPOINT ["/usr/local/bin/entrypoint-uid999.sh"]
# Docker clears inherited CMD when ENTRYPOINT changes; preserve the exact D085 command.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "17493"]
# Environment, modules, dependencies and UI remain inherited without changes.
