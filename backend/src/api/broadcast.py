
from fastapi import APIRouter
import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaBlackhole
from src.api.schemas import Offer
from src.middleware.broadcast_processing import FrameProcessor, VideoTransformTrack


router=APIRouter()
pcs = set()

@router.post("/offer")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection()
    pcs.add(pc)
    relay = MediaRelay()


    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

  
    processor = FrameProcessor("backend/src/middleware/yolo11s.pt", device="cuda")
    @pc.on("track")
    def on_track(track):
       

    
    
        if track.kind == "video":
            pc.addTrack(

                VideoTransformTrack(relay.subscribe(track),processor)#, transform=params.video_transform
            )


        @track.on("ended")
        def track_ended():
            print("[Track] Ended. Cleaning up...")
            if hasattr(processor, "close"):
                asyncio.create_task(processor.close())  # корректный shutdown
                
    

    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}





async def close_connection(pc: RTCPeerConnection):
    if pc in pcs:
        pcs.discard(pc)
    await pc.close()
    # Принудительно собираем мусор
    await asyncio.sleep(0.1)
    import gc
    gc.collect()

@router.on_event("shutdown")
async def on_shutdown():
    coros = [close_connection(pc) for pc in pcs.copy()]
    await asyncio.gather(*coros)