import { ReactElement } from 'react';

// Fix for Ant Design Icon TypeScript errors
declare module '@ant-design/icons' {
  interface IconProps {
    className?: string;
    style?: React.CSSProperties;
    spin?: boolean;
    rotate?: number;
    twoToneColor?: string;
    // Add the missing pointer event props
    onPointerEnterCapture?: React.PointerEventHandler<any>;
    onPointerLeaveCapture?: React.PointerEventHandler<any>;
    [key: string]: any;
  }

  export const MailOutlined: React.FC<IconProps>;
  export const BoxPlotOutlined: React.FC<IconProps>;
  export const DollarOutlined: React.FC<IconProps>;
  export const CalculatorOutlined: React.FC<IconProps>;
} 