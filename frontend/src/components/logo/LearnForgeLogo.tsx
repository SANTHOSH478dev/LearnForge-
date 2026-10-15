import React from 'react';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  showTagline?: boolean;
}

export const LearnForgeLogo: React.FC<LogoProps> = ({
  className = '',
  size = 'md',
  showText = true,
  showTagline = false,
}) => {
  const sizeMap = {
    sm: { icon: 'w-7 h-7', text: 'text-lg', spark: 'w-2 h-2' },
    md: { icon: 'w-9 h-9', text: 'text-xl', spark: 'w-2.5 h-2.5' },
    lg: { icon: 'w-12 h-12', text: 'text-2xl', spark: 'w-3 h-3' },
  };

  const { icon, text } = sizeMap[size];

  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      {/* Custom Icon: Book Base + Spark + Upward Progress Arrow */}
      <div className={`relative ${icon} rounded-xl bg-gradient-to-br from-violet-600 via-indigo-700 to-cyan-500 p-0.5 shadow-lg shadow-violet-500/25 flex items-center justify-center`}>
        <div className="w-full h-full bg-[#0b0f19] rounded-[10px] flex items-center justify-center relative overflow-hidden">
          {/* Subtle background glow */}
          <div className="absolute inset-0 bg-gradient-to-tr from-violet-500/20 to-cyan-500/20" />

          <svg
            className="w-5/6 h-5/6 text-white relative z-10"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Open Book Base */}
            <path
              d="M6 23C8.5 21.5 12 21.5 16 23.5C20 21.5 23.5 21.5 26 23V11C23.5 9.5 20 9.5 16 11.5C12 9.5 8.5 9.5 6 11V23Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-violet-300"
            />
            {/* Book Spine Center Divider */}
            <path
              d="M16 11.5V23.5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              className="text-indigo-400"
            />
            {/* Upward Progress Vector Rising from Center */}
            <path
              d="M16 18L16 6M16 6L12.5 9.5M16 6L19.5 9.5"
              stroke="#22D3EE"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Intelligence Spark at Apex */}
            <circle cx="16" cy="4.5" r="1.5" fill="#FDE047" />
          </svg>
        </div>
      </div>

      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-1">
            <span className={`font-bold tracking-tight text-white ${text}`}>
              Learn<span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-indigo-300 to-cyan-400">Forge</span>
            </span>
            <span className="px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-cyan-300 bg-cyan-950/80 border border-cyan-500/30 rounded-md">
              AI
            </span>
          </div>
          {showTagline && (
            <span className="text-[11px] text-zinc-400 tracking-wide font-medium">
              Turn Every Page Into Progress
            </span>
          )}
        </div>
      )}
    </div>
  );
};
