// 图表主题配置
const theme = {
    backgroundColor: 'transparent',
    textStyle: {
        color: '#ffffff'
    },
    title: {
        textStyle: {
            color: '#00e4ff'
        }
    },
    legend: {
        textStyle: {
            color: '#ffffff'
        }
    },
    xAxis: {
        axisLine: {
            lineStyle: {
                color: '#1a3969'
            }
        },
        splitLine: {
            lineStyle: {
                color: '#1a3969'
            }
        }
    },
    yAxis: {
        axisLine: {
            lineStyle: {
                color: '#1a3969'
            }
        },
        splitLine: {
            lineStyle: {
                color: '#1a3969'
            }
        }
    }
};

// 初始化所有图表
const charts = {
    trafficChart: echarts.init(document.getElementById('traffic-chart')),
    trafficPie: echarts.init(document.getElementById('traffic-pie')),
    trafficBar: echarts.init(document.getElementById('traffic-bar')),
    cpuGauge: echarts.init(document.getElementById('cpu-gauge')),
    memoryGauge: echarts.init(document.getElementById('memory-gauge')),
    swapGauge: echarts.init(document.getElementById('swap-gauge')),
    diskGauge: echarts.init(document.getElementById('disk-gauge')),
    radarChart: echarts.init(document.getElementById('radar-chart')),
    attackRate: echarts.init(document.getElementById('attack-rate')),
    domainPie: echarts.init(document.getElementById('domain-pie'))
};

// 流量趋势图配置
const trafficOption = {
    ...theme,
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: ['业务流量', '网络攻击流量', '恶意软件流量'],
        bottom: 0
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
    },
    yAxis: {
        type: 'value'
    },
    series: [
        {
            name: '业务流量',
            type: 'line',
            stack: '总量',
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(0,228,255,0.3)' },
                    { offset: 1, color: 'rgba(0,228,255,0.1)' }
                ])
            },
            lineStyle: {
                color: '#00e4ff'
            },
            data: [1500, 1450, 1500, 1480, 1520, 1500, 1550, 1500, 1520, 1500]
        },
        {
            name: '网络攻击流量',
            type: 'line',
            stack: '总量',
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(255,77,79,0.3)' },
                    { offset: 1, color: 'rgba(255,77,79,0.1)' }
                ])
            },
            lineStyle: {
                color: '#ff4d4f'
            },
            data: [200, 220, 180, 200, 180, 190, 200, 180, 190, 200]
        },
        {
            name: '恶意软件流量',
            type: 'line',
            stack: '总量',
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(250,173,20,0.3)' },
                    { offset: 1, color: 'rgba(250,173,20,0.1)' }
                ])
            },
            lineStyle: {
                color: '#faad14'
            },
            data: [300, 320, 280, 300, 280, 290, 300, 280, 290, 300]
        }
    ]
};

// 流量占比饼图配置
const pieOption = {
    ...theme,
    tooltip: {
        trigger: 'item'
    },
    series: [
        {
            type: 'pie',
            radius: '70%',
            data: [
                { value: 75, name: '业务流量', itemStyle: { color: '#00e4ff' } },
                { value: 25, name: '恶意流量', itemStyle: { color: '#ff4d4f' } }
            ],
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
};

// 流量分布柱状图配置
const barOption = {
    ...theme,
    tooltip: {
        trigger: 'axis'
    },
    xAxis: {
        type: 'category',
        data: ['业务流量', '网络攻击流量', '恶意软件流量']
    },
    yAxis: {
        type: 'value'
    },
    series: [
        {
            type: 'bar',
            data: [
                { value: 20000, itemStyle: { color: '#00e4ff' } },
                { value: 3000, itemStyle: { color: '#ff4d4f' } },
                { value: 5000, itemStyle: { color: '#faad14' } }
            ]
        }
    ]
};

// 仪表盘通用配置
function createGaugeOption(value, name, color) {
    return {
        ...theme,
        series: [
            {
                type: 'gauge',
                startAngle: 180,
                endAngle: 0,
                min: 0,
                max: 100,
                splitNumber: 8,
                axisLine: {
                    lineStyle: {
                        width: 6,
                        color: [
                            [0.3, '#67e0e3'],
                            [0.7, '#37a2da'],
                            [1, '#fd666d']
                        ]
                    }
                },
                pointer: {
                    icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
                    length: '12%',
                    width: 20,
                    offsetCenter: [0, '-60%'],
                    itemStyle: {
                        color: 'auto'
                    }
                },
                axisTick: {
                    length: 12,
                    lineStyle: {
                        color: 'auto',
                        width: 2
                    }
                },
                splitLine: {
                    length: 20,
                    lineStyle: {
                        color: 'auto',
                        width: 5
                    }
                },
                axisLabel: {
                    color: '#ffffff',
                    fontSize: 12,
                    distance: -60
                },
                title: {
                    offsetCenter: [0, '-20%'],
                    fontSize: 14,
                    color: '#ffffff'
                },
                detail: {
                    fontSize: 20,
                    offsetCenter: [0, '0%'],
                    valueAnimation: true,
                    formatter: '{value}%',
                    color: '#ffffff'
                },
                data: [{ value: value, name: name }]
            }
        ]
    };
}

// 雷达图配置
const radarOption = {
    ...theme,
    radar: {
        indicator: [
            { name: '源IP熵值', max: 10 },
            { name: '目标端口熵值', max: 10 },
            { name: 'OWCD值', max: 10 }
        ],
        splitArea: {
            areaStyle: {
                color: ['rgba(0,228,255,0.1)']
            }
        },
        axisLine: {
            lineStyle: {
                color: '#1a3969'
            }
        },
        splitLine: {
            lineStyle: {
                color: '#1a3969'
            }
        }
    },
    series: [
        {
            type: 'radar',
            data: [
                {
                    value: [6, 8, 5],
                    areaStyle: {
                        color: 'rgba(0,228,255,0.2)'
                    },
                    lineStyle: {
                        color: '#00e4ff'
                    }
                }
            ]
        }
    ]
};

// 攻击率环形图配置
const attackRateOption = {
    ...theme,
    series: [
        {
            type: 'gauge',
            radius: '100%',
            startAngle: 90,
            endAngle: -270,
            pointer: {
                show: false
            },
            progress: {
                show: true,
                overlap: false,
                roundCap: true,
                clip: false,
                itemStyle: {
                    color: '#00e4ff'
                }
            },
            axisLine: {
                lineStyle: {
                    width: 10,
                    color: [[1, '#1a3969']]
                }
            },
            splitLine: {
                show: false
            },
            axisTick: {
                show: false
            },
            axisLabel: {
                show: false
            },
            title: {
                fontSize: 14,
                offsetCenter: [0, '30%']
            },
            data: [
                {
                    value: 0.03,
                    name: '攻击率',
                    title: {
                        offsetCenter: ['0%', '-20%']
                    },
                    detail: {
                        offsetCenter: ['0%', '0%']
                    }
                }
            ],
            detail: {
                width: 50,
                height: 14,
                fontSize: 20,
                color: '#fff',
                formatter: '{value}%'
            }
        }
    ]
};

// 域名检测饼图配置
const domainPieOption = {
    ...theme,
    tooltip: {
        trigger: 'item'
    },
    legend: {
        orient: 'vertical',
        right: 10,
        top: 'center'
    },
    series: [
        {
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: false,
                position: 'center'
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: 20,
                    fontWeight: 'bold'
                }
            },
            labelLine: {
                show: false
            },
            data: [
                { value: 80, name: '正常', itemStyle: { color: '#52c41a' } },
                { value: 15, name: '可疑', itemStyle: { color: '#faad14' } },
                { value: 5, name: '恶意', itemStyle: { color: '#ff4d4f' } }
            ]
        }
    ]
};

// 设置图表配置
charts.trafficChart.setOption(trafficOption);
charts.trafficPie.setOption(pieOption);
charts.trafficBar.setOption(barOption);
charts.cpuGauge.setOption(createGaugeOption(59.02, 'CPU使用率', '#00e4ff'));
charts.memoryGauge.setOption(createGaugeOption(64.42, '内存使用率', '#00e4ff'));
charts.swapGauge.setOption(createGaugeOption(14.76, '交换区使用率', '#00e4ff'));
charts.diskGauge.setOption(createGaugeOption(60.64, '磁盘使用率', '#00e4ff'));
charts.radarChart.setOption(radarOption);
charts.attackRate.setOption(attackRateOption);
charts.domainPie.setOption(domainPieOption);

// WebSocket连接
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};

// 更新仪表盘数据
function updateDashboard(data) {
    // 更新流量趋势
    const trafficData = data.traffic;
    charts.trafficChart.setOption({
        series: [
            { data: trafficData.business },
            { data: trafficData.attack },
            { data: trafficData.malware }
        ]
    });
    
    // 更新系统资源使用率
    charts.cpuGauge.setOption({
        series: [{ data: [{ value: data.system.cpu }] }]
    });
    charts.memoryGauge.setOption({
        series: [{ data: [{ value: data.system.memory }] }]
    });
    
    // 更新攻击率
    charts.attackRate.setOption({
        series: [{ data: [{ value: data.attack_rate }] }]
    });
    
    // 更新特征数据表格
    updateFeatureTable(data.features);
    
    // 更新域名检测数据
    if (data.domain_detection) {
        updateDomainDetection(data.domain_detection);
    }
}

// 更新特征数据表格
function updateFeatureTable(features) {
    const tbody = document.getElementById('feature-data');
    tbody.innerHTML = '';
    
    features.forEach((feature, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${feature.value.toFixed(2)}</td>
            <td>
                <span class="${feature.isNormal ? 'status-normal' : 'status-error'}">
                    ${feature.isNormal ? '✓' : '✗'}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// 更新域名检测数据
function updateDomainDetection(data) {
    // 更新统计数据
    document.getElementById('total-domains').textContent = data.total;
    document.getElementById('malicious-domains').textContent = data.malicious;
    document.getElementById('suspicious-domains').textContent = data.suspicious;
    
    // 更新饼图数据
    charts.domainPie.setOption({
        series: [{
            data: [
                { value: data.normal, name: '正常', itemStyle: { color: '#52c41a' } },
                { value: data.suspicious, name: '可疑', itemStyle: { color: '#faad14' } },
                { value: data.malicious, name: '恶意', itemStyle: { color: '#ff4d4f' } }
            ]
        }]
    });
    
    // 更新域名列表
    const tbody = document.getElementById('domain-data');
    tbody.innerHTML = '';
    
    data.domains.forEach(domain => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${domain.name}</td>
            <td><span class="detection-method">${domain.method}</span></td>
            <td>
                <span class="threat-level ${getThreatLevelClass(domain.threat_level)}">
                    ${domain.threat_level}
                </span>
            </td>
            <td>${new Date(domain.timestamp).toLocaleString()}</td>
            <td>
                <span class="${domain.status === '正常' ? 'status-normal' : 'status-error'}">
                    ${domain.status}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// 获取威胁等级样式类
function getThreatLevelClass(level) {
    switch (level.toLowerCase()) {
        case '高':
            return 'high';
        case '中':
            return 'medium';
        case '低':
            return 'low';
        default:
            return '';
    }
}

// 窗口大小改变时重绘图表
window.addEventListener('resize', () => {
    Object.values(charts).forEach(chart => chart.resize());
}); 