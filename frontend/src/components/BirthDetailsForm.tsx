import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { BirthData } from '../types';
import { Compass, Calendar, Clock, MapPin, Sparkles } from 'lucide-react';

const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters.'),
  date: z.string().min(1, 'Birth date is required.').refine((val) => {
    const selectedDate = new Date(val);
    const today = new Date();
    return selectedDate <= today;
  }, { message: 'Birth date cannot be in the future.' }),
  time: z.string().optional().or(z.literal('')),
  time_unknown: z.boolean().default(false),
  place: z.string().min(2, 'Birth place city and country is required.')
}).refine((data) => {
  if (!data.time_unknown && !data.time) {
    return false;
  }
  return true;
}, {
  message: 'Please provide a birth time or select "Unknown Time".',
  path: ['time']
});

interface BirthDetailsFormProps {
  onSubmit: (data: BirthData) => void;
  initialData: BirthData | null;
}

export const BirthDetailsForm: React.FC<BirthDetailsFormProps> = ({ onSubmit, initialData }) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<BirthData>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData || {
      name: '',
      date: '',
      time: '',
      time_unknown: false,
      place: ''
    }
  });

  const timeUnknown = watch('time_unknown');

  const onFormSubmit = (data: BirthData) => {
    onSubmit(data);
  };

  return (
    <div className="w-full max-w-lg mx-auto p-6 md:p-8 rounded-3xl bg-cosmic-slate/60 border border-cosmic-gold/20 shadow-gold-glow backdrop-blur-md">
      <div className="text-center mb-8">
        <div className="inline-flex p-3 rounded-full bg-cosmic-gold/10 border border-cosmic-gold/20 text-cosmic-gold mb-3">
          <Compass className="w-8 h-8 animate-spin" style={{ animationDuration: '20s' }} />
        </div>
        <h2 className="text-3xl font-serif text-cosmic-gold tracking-wide">Cast Your Chart</h2>
        <p className="text-xs text-cosmic-lavender mt-2 font-serif italic">
          Enter your birth coordinates to map the alignments of the stars
        </p>
      </div>

      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Name input */}
        <div className="space-y-2">
          <label className="block text-xs font-serif uppercase tracking-wider text-cosmic-gold">Full Name</label>
          <div className="relative">
            <input
              type="text"
              placeholder="e.g. Aradhna Sharma"
              {...register('name')}
              className="w-full px-4 py-3 bg-cosmic-dark/80 border border-cosmic-lavender/20 rounded-xl text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:border-cosmic-gold focus:shadow-gold-glow transition"
            />
          </div>
          {errors.name && <p className="text-xs text-cosmic-gold/80 mt-1">{errors.name.message}</p>}
        </div>

        {/* Date input */}
        <div className="space-y-2">
          <label className="block text-xs font-serif uppercase tracking-wider text-cosmic-gold">Date of Birth</label>
          <div className="relative flex items-center">
            <input
              type="date"
              {...register('date')}
              className="w-full px-4 py-3 bg-cosmic-dark/80 border border-cosmic-lavender/20 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-cosmic-gold transition"
            />
            <Calendar className="absolute right-4 w-4 h-4 text-cosmic-lavender/50 pointer-events-none" />
          </div>
          {errors.date && <p className="text-xs text-cosmic-gold/80 mt-1">{errors.date.message}</p>}
        </div>

        {/* Time input + Checkbox */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="block text-xs font-serif uppercase tracking-wider text-cosmic-gold">Time of Birth</label>
            <label className="flex items-center text-xs text-cosmic-lavender cursor-pointer select-none">
              <input
                type="checkbox"
                {...register('time_unknown')}
                className="mr-2 rounded border-cosmic-lavender/30 text-cosmic-gold bg-cosmic-dark focus:ring-0"
              />
              Unknown Time
            </label>
          </div>
          
          {!timeUnknown && (
            <div className="relative flex items-center">
              <input
                type="time"
                {...register('time')}
                className="w-full px-4 py-3 bg-cosmic-dark/80 border border-cosmic-lavender/20 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-cosmic-gold transition"
              />
              <Clock className="absolute right-4 w-4 h-4 text-cosmic-lavender/50 pointer-events-none" />
            </div>
          )}
          {errors.time && <p className="text-xs text-cosmic-gold/80 mt-1">{errors.time.message}</p>}
        </div>

        {/* Birth place input */}
        <div className="space-y-2">
          <label className="block text-xs font-serif uppercase tracking-wider text-cosmic-gold">Place of Birth</label>
          <div className="relative flex items-center">
            <input
              type="text"
              placeholder="e.g. Mumbai, India"
              {...register('place')}
              className="w-full px-4 py-3 bg-cosmic-dark/80 border border-cosmic-lavender/20 rounded-xl text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:border-cosmic-gold focus:shadow-gold-glow transition"
            />
            <MapPin className="absolute right-4 w-4 h-4 text-cosmic-lavender/50 pointer-events-none" />
          </div>
          <p className="text-[10px] text-cosmic-lavender/70 italic mt-1">Provide city and country for accurate geocoding</p>
          {errors.place && <p className="text-xs text-cosmic-gold/80 mt-1">{errors.place.message}</p>}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full mt-4 py-3.5 bg-gradient-to-r from-cosmic-gold to-yellow-600 text-cosmic-dark font-serif font-semibold text-base rounded-xl hover:shadow-gold-glow active:scale-98 transition duration-200 flex items-center justify-center space-x-2 border border-cosmic-gold/30"
        >
          <Sparkles className="w-5 h-5" />
          <span>{isSubmitting ? 'Consulting Ephemeris...' : 'Align AstroAgent'}</span>
        </button>
      </form>
    </div>
  );
};
