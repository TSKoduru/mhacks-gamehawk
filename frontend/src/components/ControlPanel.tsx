import { motion } from 'motion/react';
import { Play, Pause, RotateCcw, Settings } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface ControlPanelProps {
  isPlaying: boolean;
  isPaused: boolean;
  onPlay: () => void;
  onPause: () => void;
  onReset: () => void;
  totalWords: number;
  completedWords: number;
}

export function ControlPanel({ 
  isPlaying, 
  isPaused, 
  onPlay, 
  onPause, 
  onReset,
  totalWords,
  completedWords
}: ControlPanelProps) {
  return (
    <motion.div 
      className="bg-white/95 backdrop-blur-sm rounded-2xl border border-white/30 shadow-2xl shadow-indigo-500/20 p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 text-indigo-700">
          <Settings className="w-5 h-5 text-indigo-600" />
          Robot Control
        </h3>
        <Badge variant="outline" className="bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 border-purple-300">
          CV Word Hunt Bot
        </Badge>
      </div>
      
      <div className="flex items-center gap-3 mb-4">
        <Button
          onClick={isPlaying && !isPaused ? onPause : onPlay}
          variant={isPlaying && !isPaused ? "secondary" : "default"}
          className="flex items-center gap-2"
        >
          {isPlaying && !isPaused ? (
            <>
              <Pause className="w-4 h-4" />
              Pause
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              {isPaused ? 'Resume' : 'Start'}
            </>
          )}
        </Button>
        
        <Button
          onClick={onReset}
          variant="outline"
          className="flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </Button>
      </div>
      
      <div className="space-y-2 text-sm text-muted-foreground">
        <div className="flex justify-between">
          <span>Status:</span>
          <span className={
            !isPlaying ? 'text-gray-500' :
            isPaused ? 'text-amber-600 font-medium' :
            'text-green-600 font-medium'
          }>
            {!isPlaying ? 'Stopped' : isPaused ? 'Paused' : 'Running'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Words Found:</span>
          <span>{completedWords} / {totalWords}</span>
        </div>
        <div className="flex justify-between">
          <span>Success Rate:</span>
          <span>{totalWords > 0 ? Math.round((completedWords / totalWords) * 100) : 0}%</span>
        </div>
      </div>
    </motion.div>
  );
}