import os
from pathlib import Path
from moviepy import VideoFileClip
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Tuple


def extract_audio(video_path: Path, output_path: Path, sample_rate=16000):
    video = VideoFileClip(str(video_path))
    audio = video.audio
    if audio is None:
        print(f"No audio in {video_path}")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_wav = output_path.with_suffix('.wav')
    audio.write_audiofile(
        str(final_wav),
        fps=sample_rate,
        codec='pcm_s16le',
        ffmpeg_params=['-ac', '1'],
        logger=None,
    )

async def worker(
    work_queue: asyncio.Queue[tuple[Path, Path, int] | None], 
    executor: ThreadPoolExecutor
):
    while True:
        try:
            item: Optional[Tuple[Path, Path, int]] = await asyncio.wait_for(work_queue.get(), timeout=1.0)
            if item is None:
                break
            video_path: Path
            output_path: Path
            sample_rate: int
            video_path, output_path, sample_rate = item

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, extract_audio, video_path, output_path, sample_rate)
            work_queue.task_done()
        except Exception as e:
            continue


async def batch_extract_audio_queue(
    list_of_videos: list[str], 
    output_dir: str,
    sample_rate: int = 16000, 
    num_workers: int = 2
):
    work_queue = asyncio.Queue()
    print("Extracting audio")

    for video_path in list_of_videos:
        await work_queue.put((Path(video_path), Path(output_dir), sample_rate))

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        workers: List[asyncio.Task[None]] = [
            asyncio.create_task(worker(work_queue, executor)) for _ in range(num_workers)
        ]
        await work_queue.join()
        for _ in range(num_workers):
            await work_queue.put(None)
        await asyncio.gather(*workers)
    
    
