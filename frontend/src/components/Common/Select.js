import React from 'react';
import { Select } from 'antd';
const onChange = (value) => {
  console.log(`selected ${value}`);
};
const onSearch = (value) => {
  console.log('search:', value);
};

// // Filter `option.label` match the user type `input`
// const filterOption = (input, option) =>
//   (option?.label ?? '').toLowerCase().includes(input.toLowerCase());

const filterOption = (input, option) => {
    const inputValue = input.toLowerCase();

    // 检查 label 是否包含 input
    const labelMatch = (option?.label ?? '').toLowerCase().includes(inputValue);

    // 检查 value 是否包含 input
    const valueMatch = (option?.value ?? '').toLowerCase().includes(inputValue);

    // 返回是否匹配
    return labelMatch || valueMatch;
};

const App = (props) => (
  <Select
    showSearch
    style={props.style}
    placeholder={props.placeholder}
    optionFilterProp="children"
    onChange={props.onChange}
    onSearch={props.onSearch}
    filterOption={filterOption}
    options={props.options}
  />
);
export default App;