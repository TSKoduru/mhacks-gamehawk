import { motion } from 'motion/react';
import { CheckCircle, Clock, Play } from 'lucide-react';
import { Badge } from './ui/badge';

export interface Word {
  word: string;
  coordinates: number[][];
  duration: number; // seconds to highlight
  status: 'pending' | 'playing' | 'completed';
}

interface WordListProps {
  words: Word[];
  currentWordIndex: number;
  timeRemaining: number;
}

export function WordList({ words, currentWordIndex, timeRemaining }: WordListProps) {
  return (
    <div className="bg-white/95 backdrop-blur-sm rounded-2xl border border-white/30 shadow-2xl shadow-indigo-500/20 p-6 max-w-md w-full">
      <h2 className="mb-4 flex items-center gap-2 text-indigo-700">
        <Play className="w-5 h-5 text-indigo-600" />
        Word Hunt Progress
      </h2>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {words.map((wordData, index) => (
          <motion.div
            key={wordData.word}
            className={`
              p-3 rounded-xl border transition-all duration-200
              ${index === currentWordIndex
                ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300 shadow-md'
                : wordData.status === 'completed'
                ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300 shadow-md'
                : 'bg-white/60 border-gray-200 hover:bg-white/80'
              }
            `}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium">{wordData.word.toUpperCase()}</span>
              <div className="flex items-center gap-2">
                {wordData.status === 'completed' && (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                )}
                {index === currentWordIndex && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-mono text-blue-700 font-semibold">{timeRemaining}s</span>
                  </div>
                )}
                <Badge 
                  variant="secondary"
                  className={`
                    ${wordData.status === 'completed' 
                      ? 'bg-green-100 text-green-800 border-green-200' :
                      index === currentWordIndex 
                      ? 'bg-blue-100 text-blue-800 border-blue-200' :
                      'bg-gray-100 text-gray-600 border-gray-200'
                    }
                  `}
                >
                  {wordData.status === 'completed' ? 'Done' :
                   index === currentWordIndex ? 'Playing' :
                   'Pending'}
                </Badge>
              </div>
            </div>
            
            {index === currentWordIndex && (
              <motion.div 
                className="mt-2 h-1 bg-secondary rounded-full overflow-hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
                  initial={{ width: '100%' }}
                  animate={{ width: `${(timeRemaining / wordData.duration) * 100}%` }}
                  transition={{ duration: 0.1 }}
                />
              </motion.div>
            )}
            
            <div className="mt-2 text-sm text-muted-foreground">
              Path: {wordData.coordinates.map(([r, c]) => `(${r},${c})`).join(' → ')}
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-muted rounded-lg">
        <div className="flex justify-between text-sm">
          <span>Progress:</span>
          <span>{words.filter(w => w.status === 'completed').length} / {words.length} words</span>
        </div>
        <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all duration-500"
            style={{ width: `${(words.filter(w => w.status === 'completed').length / words.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}