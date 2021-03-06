

export const MathUtils = {
    
    TAU: 2 * Math.PI,
    
    rad2deg: function(radians: number): number {
        return radians * 180 / Math.PI;
    },
    
    deg2rad: function(degrees: number): number {
        return degrees * Math.PI / 180;
    },
    
    randomRange: function(min: number, max: number): number {
        return Math.random() * (max - min) + min;
    },
    
    angleToString: function(angle: number): string {
        if (angle < 0) {
            angle += MathUtils.TAU;
        }
        return MathUtils.rad2deg(angle).toFixed(2) + "°";
    },
    
};

export const isFunction = function(o) {
    return !!(o && o.constructor && o.call && o.apply);
};

export interface TextElement {
    
    innerText: string;
    
}

class NullTextElement implements TextElement {
    
    set innerText(text: string) {
        // do nothing
    }
    
}

export const nullTextElement = new NullTextElement();