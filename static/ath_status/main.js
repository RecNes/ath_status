// main.js - ath_status

function getCookie(name) {
    if (!document.cookie) {
        return null;
    }
    const xsrfCookies = document.cookie.split(';')
        .map(c => c.trim());
    // ... Eğer başka bir işlem gerekiyorsa buraya ekleyin ...
}

function getLast30Days() {
    let days = [];
    let now = new Date();
    for (let i = 29; i >= 0; i--) {
        let d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
        let yyyy = d.getFullYear();
        let mm = String(d.getMonth() + 1).padStart(2, '0');
        let dd = String(d.getDate()).padStart(2, '0');
        let formatted = `${yyyy}-${mm}-${dd}`;
        days.push(formatted);
    }
    return days;
}

function getXValues(data) {
    return getLast30Days();
}

function getYValues(data) {
    let days = getLast30Days();
    let ratesByDay = {};
    data.forEach(item => {
        let d = new Date(item.record_date);
        let yyyy = d.getFullYear();
        let mm = String(d.getMonth() + 1).padStart(2, '0');
        let dd = String(d.getDate()).padStart(2, '0');
        let formatted = `${yyyy}-${mm}-${dd}`;
        ratesByDay[formatted] = Number(item.exchange_rate);
    });
    let rateList = [];
    let lastRate = 0;
    days.forEach(day => {
        if (ratesByDay.hasOwnProperty(day)) {
            lastRate = ratesByDay[day];
            rateList.push(lastRate);
        } else {
            rateList.push(lastRate);
        }
    });
    return rateList;
}

let allChartData = {};
let bigChart = null;
let bigChartId = null;

function drawCharts() {
    fetch('/get-all-chart-data/')
        .then(response => {
            if (!response.ok) {
                console.error('get-all-chart-data endpoint error:', response.status, response.statusText);
                throw new Error('get-all-chart-data endpoint error');
            }
            return response.json();
        })
        .then(allData => {
            allChartData = allData;
            let chartCanvases = document.getElementsByClassName('currency-chart');
            Array.prototype.forEach.call(chartCanvases, function (item) {
                let id = item.dataset.id;
                let data = allData[id] || [];
                let xValues = getXValues(data);
                let yValues = getYValues(data);
                let chart = new Chart(item, {
                    type: 'line',
                    data: {
                        labels: xValues,
                        datasets: [{
                            data: yValues,
                            borderColor: '#3a5fc8',
                            backgroundColor: 'rgba(58,95,200,0.08)',
                            pointRadius: 2,
                            lineTension: 0.2
                        }]
                    },
                    options: {
                        legend: {
                            display: false
                        },
                        scales: {
                            xAxes: [{
                                type: 'category',
                                ticks: {
                                    autoSkip: true,
                                    maxTicksLimit: 30,
                                    fontColor: '#2d3e5e',
                                    fontSize: 10
                                },
                                gridLines: {
                                    display: false
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    fontColor: '#2d3e5e',
                                    fontSize: 10
                                },
                                gridLines: {
                                    color: '#e3eafc'
                                }
                            }]
                        },
                        tooltips: {
                            callbacks: {
                                title: function (tooltipItems, data) {
                                    return 'Gün: ' + tooltipItems[0].label;
                                },
                                label: function (tooltipItem, data) {
                                    return 'ATH: ' + tooltipItem.value;
                                }
                            }
                        }
                    }
                });
                chart.update();
                item.onclick = function () {
                    showBigChart(id);
                };
            });
            if (bigChartId) {
                updateBigChart(bigChartId);
            }
        })
        .catch(error => {
            console.error('fetch get-all-chart-data error:', error);
        });
}

function showBigChart(id) {
    bigChartId = id;
    let modal = document.getElementById('big-chart-modal');
    let canvas = document.getElementById('big-chart-canvas');
    let title = document.getElementById('big-chart-title');
    if (bigChart) {
        bigChart.destroy();
    }
    let data = allChartData[id] || [];
    let xValues = getXValues(data);
    let yValues = getYValues(data);
    bigChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: xValues,
            datasets: [{
                data: yValues,
                borderColor: '#3a5fc8',
                backgroundColor: 'rgba(58,95,200,0.08)',
                pointRadius: 3,
                lineTension: 0.2
            }]
        },
        options: {
            legend: { display: false },
            scales: {
                xAxes: [{
                    type: 'category',
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 30,
                        fontColor: '#2d3e5e',
                        fontSize: 14
                    },
                    gridLines: { display: false }
                }],
                yAxes: [{
                    ticks: {
                        fontColor: '#2d3e5e',
                        fontSize: 14
                    },
                    gridLines: { color: '#e3eafc' }
                }]
            },
            tooltips: {
                callbacks: {
                    title: function (tooltipItems, data) {
                        return 'Gün: ' + tooltipItems[0].label;
                    },
                    label: function (tooltipItem, data) {
                        return 'ATH: ' + tooltipItem.value;
                    }
                }
            }
        }
    });
    // Başlık güncelle
    if (title) {
        let row = document.querySelector('canvas[data-id="' + id + '"]').closest('tr');
        if (row) {
            let currencyCell = row.querySelector('td');
            if (currencyCell) {
                title.textContent = currencyCell.textContent.trim();
            }
        }
    }
    modal.style.display = 'flex';
}

function updateBigChart(id) {
    if (!bigChart) return;
    let data = allChartData[id] || [];
    let xValues = getXValues(data);
    let yValues = getYValues(data);
    bigChart.data.labels = xValues;
    bigChart.data.datasets[0].data = yValues;
    bigChart.update();
}

function updateNumbers() {
    fetch(window.location.pathname, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, 'text/html');
            ['current-rate', 'ath-rate', 'lowest-rate'].forEach(function (prefix) {
                let newCells = doc.querySelectorAll('td[id^="' + prefix + '-"]');
                newCells.forEach(function (newCell) {
                    let id = newCell.id;
                    let oldCell = document.getElementById(id);
                    if (oldCell) {
                        oldCell.innerHTML = newCell.innerHTML;
                        oldCell.title = newCell.title;
                    }
                });
            });
        });
}

let autoRefreshInterval = null;
let currentIntervalMin = 5;

function setAutoRefreshInterval(minutes) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    autoRefreshInterval = setInterval(function () {
        drawCharts();
        updateNumbers();
    }, minutes * 60 * 1000);
    currentIntervalMin = minutes;
}

function startAutoRefresh() {
    setAutoRefreshInterval(currentIntervalMin);
    document.getElementById('update-interval').addEventListener('change', function (e) {
        let min = parseInt(e.target.value);
        setAutoRefreshInterval(min);
    });
}
