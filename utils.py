def record_audio(key):
    import time

    st.markdown("🎙️ Please record your answer using the microphone below:")

    rtc_config = {
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }

    ctx = webrtc_streamer(
        key=f"webrtc-{key}",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=rtc_config,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=AudioProcessor,
    )

    audio_path = None
    timeout_seconds = 10

    if ctx.state.playing:
        st.info("⏺️ Recording... Speak now.")

        # Wait up to 10s for audio frames
        start_time = time.time()
        while ctx.audio_receiver is None and time.time() - start_time < timeout_seconds:
            time.sleep(0.2)

    if ctx.audio_receiver:
        processor = ctx.audio_processor
        if processor and processor.recorded_frames:
            audio_data = np.concatenate(processor.recorded_frames, axis=0).astype(np.int16)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                sf.write(f.name, audio_data, 48000)
                audio_path = f.name
                st.success("✅ Recording complete!")
                return audio_path

    # === Fallback: File upload if recording failed ===
    st.warning("🎙️ WebRTC recording not available. Please upload a recorded audio file.")
    uploaded = st.file_uploader("📁 Upload your voice answer (MP3/WAV/WebM)", type=["mp3", "wav", "webm"], key=f"fallback-{key}")
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded.name.split('.')[-1]}") as f:
            f.write(uploaded.read())
            return f.name

    return None
