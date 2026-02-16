import React from 'react';
import { ThemeCard } from './ThemeCard';
import { MOCK_THEMES } from '../../data/themes';
import { InvestmentTheme } from '../../types';

interface ThemeListProps {
    onThemeSelect?: (theme: InvestmentTheme) => void;
}

export const ThemeList: React.FC<ThemeListProps> = ({ onThemeSelect }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-1">
            {MOCK_THEMES.map(theme => (
                <ThemeCard
                    key={theme.id}
                    theme={theme}
                    onClick={onThemeSelect}
                />
            ))}
        </div>
    );
};
