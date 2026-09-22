/**
 * Dialogue Audio Player Controller
 * Handles audio playback for Dorothy, Jiny, and Toto dialogues across markdown documents.
 */
(function () {
  function initDialogueAudioPlayers() {
    const players = document.querySelectorAll('.dialogue-audio-player');
    if (!players || players.length === 0) return;

    function setButtonState(btn, isPlaying) {
      if (!btn) return;
      if (isPlaying) {
        btn.innerHTML = '<span>⏸️ 일시정지</span>';
        btn.style.background = '#0ea5e9';
      } else {
        btn.innerHTML = '<span>▶️ 재생</span>';
        btn.style.background = '#0284c7';
      }
    }

    function stopAllOtherPlayers(currentPlayer) {
      players.forEach(function (otherPlayer) {
        if (otherPlayer !== currentPlayer) {
          const otherAudio = otherPlayer.querySelector('audio');
          const otherPlayBtn = otherPlayer.querySelector('.btn-audio-play') || otherPlayer.querySelector('button');
          if (otherAudio && !otherAudio.paused) {
            otherAudio.pause();
            otherAudio.currentTime = 0;
            setButtonState(otherPlayBtn, false);
          }
        }
      });
    }

    players.forEach(function (player) {
      const audio = player.querySelector('audio');
      const playBtn = player.querySelector('.btn-audio-play') || player.querySelector('button:first-of-type');
      const stopBtn = player.querySelector('.btn-audio-stop') || player.querySelector('button:last-of-type');

      if (!audio || !playBtn) return;

      // Play / Pause toggle button
      playBtn.addEventListener('click', function () {
        if (audio.paused) {
          stopAllOtherPlayers(player);
          audio.play().then(function () {
            setButtonState(playBtn, true);
          }).catch(function (err) {
            console.error('Audio playback failed:', err);
            setButtonState(playBtn, false);
          });
        } else {
          audio.pause();
          setButtonState(playBtn, false);
        }
      });

      // Stop button
      if (stopBtn && stopBtn !== playBtn) {
        stopBtn.addEventListener('click', function () {
          audio.pause();
          audio.currentTime = 0;
          setButtonState(playBtn, false);
        });
      }

      // Reset when audio finishes
      audio.addEventListener('ended', function () {
        audio.currentTime = 0;
        setButtonState(playBtn, false);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDialogueAudioPlayers);
  } else {
    initDialogueAudioPlayers();
  }
})();
