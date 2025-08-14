function clearStorage() {
    localStorage.clear();
}

function getAllItemsJSON(){
    const items = { ...localStorage };
    return items;
}

export {clearStorage, getAllItemsJSON};