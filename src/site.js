window.initYoutubeEmbed = function initYoutubeEmbed(iframe, cid) {
    const feedUrl = "https://api.rss2json.com/v1/api.json?rss_url=" + encodeURIComponent("https://www.youtube.com/feeds/videos.xml?channel_id=") + cid;
    $.getJSON(feedUrl, function (data) {
        const videoUrl = data.items[0].link;
        const videoId = videoUrl.substr(videoUrl.indexOf("=") + 1);
        iframe.src = "https://youtube.com/embed/" + videoId + "?controls=0";
    });
}