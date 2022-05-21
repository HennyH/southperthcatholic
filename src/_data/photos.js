const fs = require("node:fs/promises");

module.exports = async function() {
    const folders = {
        photos: "assets/images/photos",
        saints: "assets/images/saints",
        solemnities: "assets/images/solemnities",
    }

    const photos = {};

    for (const name in folders) {
        const path = folders[name];
        const files = await fs.readdir(path);
        photos[name] = files.map(n => `${path}/${n}`);
    }

    return photos;
}