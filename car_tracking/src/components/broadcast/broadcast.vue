<template>
<div class="broadcast-container">
    <div>
        
        <audio id="audio" autoplay="true"></audio>
        <video id="video" autoplay="true"  playsinline="true"></video>
    </div>
    <div>
        <Button id="start" label="Запустить" @click="start()"  />
        <Button id="stop" label="Стоп" style="display: none" @click="stop()"></Button>
    </div>
    <div>
        <Checkbox inputId="useaudio" value="Cheese" v-model="audio_checked" binary  />
        <label for="useaudio"> Микрофон </label>
    </div>
    
    
    
</div>
</template>
<script setup lang="js">
import { ref } from "vue";
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';

var audio_checked=ref(false)

var pc = null;

// data channel
var dc = null, dcInterval = null;

function createPeerConnection() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    

    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video')
            document.getElementById('video').srcObject = evt.streams[0];
        else
            document.getElementById('audio').srcObject = evt.streams[0];
    });

    return pc;
}

function negotiate() {
    return pc.createOffer().then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        
        return fetch('http://127.0.0.1:8000/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
                // video_transform: document.getElementById('video-transform').value
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
       
        return pc.setRemoteDescription(answer);
    }).catch(function(e) {
        alert(e);
    });
}

function start() {
    document.getElementById('start').style.display = 'none';

    pc = createPeerConnection();

   

    var constraints = {
        audio: false,
        video: true
    };

    

    if (constraints.audio || constraints.video) {
        navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
            stream.getTracks().forEach(function(track) {
                pc.addTrack(track, stream);
            });
            return negotiate();
        }, function(err) {
            alert('Could not acquire media: ' + err);
        });
    } else {
        negotiate();
    }

    document.getElementById('stop').style.display = 'inline-block';
}



function stop() {
    document.getElementById('stop').style.display = 'none';
    document.getElementById('start').style.display = 'inline-block';
    // close data channel
    

    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function(transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }

    // close local audio / video
    pc.getSenders().forEach(function(sender) {
        sender.track.stop();
    });

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
}




</script>





<style>
.broadcast-container{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh; /* центрирование по всей высоте экрана */

    flex-direction: column;
    gap: 5px;
}


</style>