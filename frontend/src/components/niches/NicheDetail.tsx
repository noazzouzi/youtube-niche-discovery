import React from 'react';
import { useParams } from 'react-router-dom';

const NicheDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Niche Detail</h2>
        <p className="text-gray-600">Detailed view of niche #{id}</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-500 text-center py-8">
          Niche detail component will be implemented here.
        </p>
      </div>
    </div>
  );
};

export default NicheDetail;