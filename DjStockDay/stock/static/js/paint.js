export function MAFunc(data0, v1, v2) {
    return {
        name: v1,
        type: 'line',
        data: calculateMA(data0, v2),
        smooth: true,
        showSymbol: false,
        lineStyle: {
            normal: {
                width: 1
            }
        }
    };
}

export function calculateMA(data0, dayCount) {
    let result = [];
    for (let i = 0, len = data0.values.length; i < len; i++) {
        if (i < dayCount) {
            result.push('-');
            continue;
        }
        let sum = 0;
        for (let j = 0; j < dayCount; j++) {
            sum += +data0.values[i - j][1];
        }
        result.push(sum / dayCount);
    }
    return result;
}