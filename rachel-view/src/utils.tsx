import { COLORS } from './styles';
import CheckIcon from '@mui/icons-material/Check';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import WarningOutlinedIcon from '@mui/icons-material/WarningOutlined';

export const getSeverityBGColor = (severity: number): string => {
    // if (severity >= 8) return COLORS.severity.background.high;
    // if (severity >= 4) return COLORS.severity.background.medium;
    // return COLORS.severity.background.low;
    return 'transparent';
}

export const getSeverityTextColor = (severity: number): string => {
    if (severity >= 8) return COLORS.severity.text.high;
    if (severity >= 4) return COLORS.severity.text.medium;
    return COLORS.severity.text.low;
}

export const getSeverityIcon = (severity: number) => {
    if (severity >= 8) return <CloseOutlinedIcon sx={{ fontSize: '4rem' }} />;
    if (severity >= 4) return <WarningOutlinedIcon sx={{ fontSize: '3.2rem' }} />;
    return <CheckIcon sx={{ fontSize: '3.2rem' }} />;
}

export const getSeverityBorder = (severity: number): string => {
    // if (severity >= 8) return COLORS.severity.border.high;
    // if (severity >= 4) return COLORS.severity.border.medium;
    // return COLORS.severity.border.low;
    return 'none'
}

/**
 * Blends two colors (hex, rgb, or rgba) based on percent, returning a hex color.
 * @param baseColor - Base color string ("#f00", "rgb(...)", or "rgba(...)")
 * @param targetColor - Target color string
 * @param percent - Blend amount (0 to 1)
 * @returns Blended hex color string
 */
export const prgba = (
    baseColor: string,
    targetColor: string,
    percent: number
): string => {
    const clamp = (val: number, min = 0, max = 255) =>
        Math.max(min, Math.min(max, val));

    const parseColor = (input: string) => {
        input = input.trim().toLowerCase();

        if (input.startsWith('#')) {
            const hex = input.replace('#', '');
            const full = hex.length === 3
                ? hex.split('').map(c => c + c).join('')
                : hex;
            const bigint = parseInt(full, 16);
            return {
                r: (bigint >> 16) & 255,
                g: (bigint >> 8) & 255,
                b: bigint & 255
            };
        }

        const rgbRegex = /^rgba?\(([^)]+)\)$/;
        const match = input.match(rgbRegex);
        if (match) {
            const parts = match[1].split(',').map(x => parseFloat(x.trim()));
            return { r: parts[0], g: parts[1], b: parts[2] };
        }

        throw new Error(`Unsupported color format: ${input}`);
    };

    const rgbToHex = (r: number, g: number, b: number) =>
        '#' + [r, g, b].map(x => {
            const hex = clamp(Math.round(x)).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');

    const base = parseColor(baseColor);
    const target = parseColor(targetColor);

    const blended = {
        r: base.r + (target.r - base.r) * percent,
        g: base.g + (target.g - base.g) * percent,
        b: base.b + (target.b - base.b) * percent
    };

    return rgbToHex(blended.r, blended.g, blended.b);
};

