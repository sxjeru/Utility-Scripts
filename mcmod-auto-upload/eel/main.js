function generateTable(list) {
    var header = ["mod slug", "已上传"];
    var table = document.createElement("table");
    var headerRow = table.insertRow();
    for (var j = 0; j < header.length; j++) {
        var headerCell = document.createElement("th");
        headerCell.innerHTML = header[j];
        headerRow.appendChild(headerCell);
    }
    for (var i = 0; i < list.length; i++) {
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.innerHTML = list[i];
        var cell2 = row.insertCell();
        cell2.innerHTML = "";
    }
    return table;
}

eel.expose(createTable);
function createTable(list) {
    var tableContainer = document.getElementById("tableContainer");
    var table = generateTable(list);
    tableContainer.appendChild(table);

    var pg = document.getElementById("pg-text");
    pg.textContent = "0 / " + list.length;
}

eel.expose(addLog);
function addLog(msg) {
    var logBox = document.getElementById("log");
    logBox.textContent += msg + "\n";
    logBox.scrollTop = logBox.scrollHeight;
}

function tickRow(rowNumber, x) {
    var table = document
        .getElementById("tableContainer")
        .getElementsByTagName("table")[0];
    var rowToTick = table.rows[rowNumber];
    if (rowToTick) {
        if (x == 1) {
            rowToTick.cells[1].innerHTML = "&#10003;";
        } else if (x == 2) {
            rowToTick.cells[1].innerHTML = "&#8420;";
        }
    }
}

eel.expose(urlRow);
function urlRow(rowNumber, url) {
    var table = document
        .getElementById("tableContainer")
        .getElementsByTagName("table")[0];
    var row = table.rows[rowNumber];
    if (row) {
        var cell = row.cells[0];
        var link = document.createElement("a");
        link.href = url;
        link.target = "_blank";
        link.rel = "noreferrer";
        link.textContent = cell.textContent;
        cell.innerHTML = "";
        cell.appendChild(link);
    }
}

eel.expose(update);
function update(a, b, x) {
    var pg = document.getElementsByClassName('pg');
    width = a / b * 100;
    pg[0].style.width = width.toString() + "%";
    if (width > 90) {
        pg[0].style.borderRadius = '25px 25px 25px 25px';
    }

    var pg = document.getElementById("pg-text");
    pg.textContent = a + " / " + b;

    tickRow(a, x);
}

eel.expose(mcmod);
function mcmod(url) {
    var mcmod = document.getElementById("mcmod");
    mcmod.src = url;
}

eel.expose(option);
function option(url) {
    var opt1 = document.getElementById('opt1').value;
    var opt2 = document.getElementById('opt2').checked; // true
    return { opt1: opt1, opt2: opt2 };
}

// eel.main();

// const links = document.querySelectorAll('a');
// links.forEach(link => {
// 	link.addEventListener('click', function() {
// 		this.classList.add('clicked');
// 	});
// });
