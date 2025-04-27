import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';

export default function NavBar() {
  const [username, setUsername] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem('access_token');

  // Хук теперь всегда на своих местах
  useEffect(() => {
    if (!token) {
      setUsername('');
      return;
    }
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUsername(payload.username || '');
    } catch {
      setUsername('');
    }
  }, [location.pathname, token]);

  // Не показываем шапку на странице логина
  if (location.pathname === '/login') return null;

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login', { replace: true });
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          {username ? `Привет, ${username}` : 'CV Diagnostics'}
        </Typography>
        {token && (
          <Button color="inherit" onClick={handleLogout}>
            Выйти
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
