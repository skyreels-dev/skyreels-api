        """Minimal SkyReels example: create one prediction and print the output URL(s)."""
        import skyreels_api

        output = skyreels_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
        print(output)
