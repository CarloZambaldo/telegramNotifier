async def _forward_output(self, chat_id: int) -> None:
    """Forward subprocess output back to the chat."""

    assert self.active_process is not None
    proc = self.active_process
    while proc and not proc.stdout.at_eof():
        line = await proc.stdout.readline()
        if line:
            await self.app.bot.send_message(chat_id, line.decode().rstrip())
    if proc:
        code = await proc.wait()
        await self.app.bot.send_message(
            chat_id, f"Process finished with code {code}"
        )
    self.active_process = None
