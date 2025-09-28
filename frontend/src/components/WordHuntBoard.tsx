import { motion } from 'motion/react';

interface WordHuntBoardProps {
  board: string[][];
  highlightedTiles: number[][];
  currentWord?: string;
}

export function WordHuntBoard({ board, highlightedTiles, currentWord }: WordHuntBoardProps) {
  const isHighlighted = (row: number, col: number) => {
    return highlightedTiles.some(([r, c]) => r === row && c === col);
  };

  return (
    <div className="flex flex-col items-center space-y-6">
      <div className="grid grid-cols-4 gap-3 p-8 bg-white/95 backdrop-blur-sm rounded-2xl border border-white/30 shadow-2xl shadow-indigo-500/20">
        {board.map((row, rowIndex) =>
          row.map((letter, colIndex) => (
            <motion.div
              key={`${rowIndex}-${colIndex}`}
              className={`
                w-24 h-24 flex items-center justify-center rounded-lg border-2 transition-all duration-300 text-3xl font-semibold
                ${isHighlighted(rowIndex, colIndex)
                  ? 'text-white border-yellow-400 shadow-2xl scale-105 shadow-yellow-400/50'
                  : 'border-white/30 hover:border-indigo-300 hover:scale-102 shadow-lg backdrop-blur-sm'
                }
              `}
              style={{
                background: isHighlighted(rowIndex, colIndex) 
                  ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'
                  : 'rgba(255, 255, 255, 0.9)'
              }}
              initial={{ scale: 1 }}
              animate={{ 
                scale: isHighlighted(rowIndex, colIndex) ? 1.05 : 1,
                rotateY: isHighlighted(rowIndex, colIndex) ? [0, 10, 0] : 0
              }}
              transition={{ duration: 0.3, type: "spring", stiffness: 300 }}
            >
              {letter.toUpperCase()}
            </motion.div>
          ))
        )}
      </div>
      {currentWord && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl shadow-lg font-medium"
        >
          Currently finding: <span className="font-semibold">{currentWord.toUpperCase()}</span>
        </motion.div>
      )}
    </div>
  );
}