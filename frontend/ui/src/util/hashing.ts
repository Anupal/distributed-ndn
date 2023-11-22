//From: https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
//We only need this to generate keys for one of our list in the UI
export function hashCode(str: string): number {
    return str.split('').reduce((prevHash, currVal) =>
        (((prevHash << 5) - prevHash) + currVal.charCodeAt(0))|0, 0);
}
