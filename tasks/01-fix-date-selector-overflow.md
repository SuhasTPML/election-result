# Task: Fix Date Selector Overflow Issue

## Description
The date selector (year buttons) at the top of the parliament chart was going outside of the image box/container, causing layout issues.

## Problem
- Year buttons were not properly contained within the chart container
- Buttons were overflowing the designated area
- Layout was inconsistent on different screen sizes

## Solution
Updated the CSS styling for the controls container and buttons:

```css
.controls { 
  width: 100%; 
  max-width: 900px; 
  text-align: left; 
  margin-bottom: 20px; 
  display: flex; 
  flex-wrap: wrap; 
  gap: 4px;
}

.controls button { 
  padding: 8px 16px; 
  margin: 0; 
  font-size: 16px; 
  border: 1px solid #ccc; 
  background-color: #f0f0f0; 
  border-radius: 4px; 
  cursor: pointer; 
  transition: background-color 0.2s, color 0.2s; 
  flex: 0 0 auto; 
}
```

## Files Modified
- `config.html` - Updated CSS styles

## Verification
- Buttons now stay within the chart container bounds
- Buttons wrap to next line when needed
- Layout is consistent across different screen sizes