
document.querySelectorAll('video, audio').forEach(videoEle => {
    // 静音
    //  muted 有时候会导致暂停, ?
    videoEle.muted = true
    videoEle.volume = 0
});


const runMute = () => {
                        // 立即设置全局静音
                        window.audioContexts = [];

                        // 重写 AudioContext 构造函数
                        const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
                        if (OriginalAudioContext) {
                            window.AudioContext = window.webkitAudioContext = function() {
                                const ctx = new OriginalAudioContext();
                                ctx.createGain = function() {
                                    const gainNode = OriginalAudioContext.prototype.createGain.call(this);
                                    gainNode.gain.value = 0;
                                    return gainNode;
                                };
                                window.audioContexts.push(ctx);
                                return ctx;
                            };
                        }

                        // 静音现有视频/音频元素
                        const muteAllMedia = () => {
                            document.querySelectorAll('video, audio').forEach(media => {
                                media.muted = true;
                                media.volume = 0;

                                // 防止自动播放
                                media.autoplay = false;
                                media.pause();

                                // 阻止媒体播放事件
                                const originalPlay = media.play;
                                media.play = function() {
                                    this.muted = true;
                                    this.volume = 0;
                                    return originalPlay.call(this).then(() => {
                                        this.muted = true;
                                        this.volume = 0;
                                    });
                                };
                            });
                        };

                        // 初始静音
                        muteAllMedia();

                        // 监听 DOM 变化，静音新添加的媒体元素
                        const observer = new MutationObserver(muteAllMedia);
                        observer.observe(document.body, {
                            childList: true,
                            subtree: true
                        });

                        // 拦截 Web Audio API
                        if (window.AudioContext) {
                            const originalCreateGain = AudioContext.prototype.createGain;
                            AudioContext.prototype.createGain = function() {
                                const gainNode = originalCreateGain.call(this);
                                gainNode.gain.value = 0;
                                return gainNode;
                            };
                        }
                    }
